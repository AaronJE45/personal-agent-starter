"""Maintainer-only offline regression tests; not student grading or site feedback."""
import hashlib
import hmac
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
MODULE_NAMES = ('config', 'storage', 'tools', 'agent', 'whatsapp_server')


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(ROOT / 'solutions' / 'module_6')
        sys.path.insert(0, self.path)
        for name in MODULE_NAMES:
            sys.modules.pop(name, None)
        self.config = importlib.import_module('config')
        self.config.DB_PATH = Path(self.temp.name) / 'private' / 'agent.sqlite3'
        self.config.GEMINI_API_KEY = 'fake-test-key'
        self.config.GEMINI_MODEL = 'test-model'
        self.storage = importlib.import_module('storage')
        self.tools = importlib.import_module('tools')
        self.agent = importlib.import_module('agent')
        self.web = importlib.import_module('whatsapp_server')
        self.config.WHATSAPP_VERIFY_TOKEN = 'verify-test'
        self.config.WHATSAPP_APP_SECRET = 'secret-test'
        self.config.WHATSAPP_PHONE_NUMBER_ID = '123'
        self.config.WHATSAPP_ALLOWED_SENDER = '15550000000'
        self.client = self.web.app.test_client()

    def tearDown(self):
        self.web.worker.shutdown(wait=True)
        sys.path.remove(self.path)
        for name in MODULE_NAMES:
            sys.modules.pop(name, None)
        self.temp.cleanup()

    def test_persistence_and_user_isolation(self):
        first = self.tools.add_task('Learn Python', user_id='alice')
        self.tools.add_task('Other task', user_id='bob')
        self.tools.save_note('Remember 100% of SQL _ examples', user_id='alice')
        self.assertEqual(self.tools.list_tasks(user_id='alice')[0]['title'], 'Learn Python')
        self.assertFalse(self.tools.complete_task(first['id'], user_id='bob')['completed'])
        self.assertTrue(self.tools.complete_task(first['id'], user_id='alice')['completed'])
        importlib.reload(self.storage)
        self.assertTrue(self.tools.list_tasks(user_id='alice')[0]['completed'])
        self.assertEqual(len(self.tools.search_notes('%', user_id='alice')), 1)
        self.assertEqual(self.tools.search_notes('%', user_id='bob'), [])
        self.assertEqual(self.tools.search_notes("' OR 1=1 --", user_id='alice'), [])
        for value in ('', '  ', None, 123):
            with self.assertRaises(ValueError):
                self.tools.add_task(value)
        for value in (True, -1, 1.5, '1'):
            with self.assertRaises(ValueError):
                self.tools.complete_task(value)

    def test_agent_loop_preserves_content_and_scopes_tools(self):
        content = {'role': 'model', 'parts': [{'functionCall': {'name': 'add_task', 'args': {'title': 'Read'}, 'id': 'call-1'}, 'thoughtSignature': 'preserve-me'}]}
        answer = {'role': 'model', 'parts': [{'text': 'Saved.'}]}
        instance = self.agent.Agent()
        with patch.object(self.agent, 'request_model', side_effect=[content, answer]) as model:
            self.assertEqual(instance.chat('Save a task', user_id='alice'), 'Saved.')
            # Actual recorded history preserves raw provider signatures/IDs.
            history = instance.history['alice'][0]
            self.assertEqual(history[1], content)
            self.assertEqual(history[2]['parts'][0]['functionResponse']['id'], 'call-1')
        self.assertEqual(len(self.tools.list_tasks(user_id='alice')), 1)
        self.assertEqual(self.tools.list_tasks(user_id='bob'), [])
        forged = {'role': 'model', 'parts': [{'functionCall': {'name': 'add_task', 'args': {'title': 'Bad', 'user_id': 'bob'}}}]}
        with patch.object(self.agent, 'request_model', side_effect=[forged, answer]):
            instance.chat('Try forged user', user_id='alice')
        self.assertEqual(self.tools.list_tasks(user_id='bob'), [])
        error_result = instance.history['alice'][-1][2]['parts'][0]['functionResponse']['response']
        self.assertIn('error', error_result['result'])

    def test_history_limit_reset_and_step_limit(self):
        instance = self.agent.Agent()
        with patch.object(self.agent, 'request_model', return_value={'role': 'model', 'parts': [{'text': 'OK'}]}):
            for _ in range(12):
                instance.chat('Hello', user_id='alice')
        self.assertEqual(len(instance.history['alice']), self.config.MAX_HISTORY_TURNS)
        self.tools.add_task('Keep me', user_id='alice')
        self.assertIn('cleared', instance.chat('/reset', user_id='alice'))
        self.assertNotIn('alice', instance.history)
        self.assertEqual(len(self.tools.list_tasks(user_id='alice')), 1)
        call = {'role': 'model', 'parts': [{'functionCall': {'name': 'list_tasks', 'args': {}}}]}
        with patch.object(self.agent, 'request_model', return_value=call) as model:
            self.assertIn('step limit', instance.chat('Loop'))
            self.assertEqual(model.call_count, self.config.MAX_STEPS)

    def test_provider_errors_are_readable_and_hide_secrets(self):
        for code in (400, 403, 404, 429, 500):
            with patch.object(self.agent.requests, 'post', return_value=Mock(status_code=code)):
                with self.assertRaises(self.agent.AgentError) as caught:
                    self.agent.request_model([])
                self.assertNotIn('fake-test-key', str(caught.exception))
        with patch.object(self.agent.requests, 'post', return_value=Mock(status_code=200, json=lambda: {'candidates': []})):
            with self.assertRaises(self.agent.AgentError):
                self.agent.request_model([])

    def signed_post(self, data):
        raw = json.dumps(data).encode()
        signature = 'sha256=' + hmac.new(b'secret-test', raw, hashlib.sha256).hexdigest()
        return self.client.post('/webhook', data=raw, content_type='application/json', headers={'X-Hub-Signature-256': signature})

    def event(self, sender='15550000000', phone='123'):
        return {'entry': [{'changes': [{'value': {'metadata': {'phone_number_id': phone}, 'messages': [{'id': 'message-1', 'from': sender, 'type': 'text', 'text': {'body': 'hello'}}]}}]}]}

    def test_webhook_verification_and_signatures(self):
        self.assertEqual(self.client.get('/webhook?hub.mode=subscribe&hub.verify_token=verify-test&hub.challenge=abc').data, b'abc')
        self.assertEqual(self.client.get('/webhook?hub.mode=subscribe&hub.verify_token=wrong').status_code, 403)
        self.assertEqual(self.client.post('/webhook', json={}).status_code, 403)
        self.assertEqual(self.signed_post([]).status_code, 400)
        self.assertEqual(self.signed_post({'entry': [None]}).status_code, 400)
        with patch.object(self.web.worker, 'submit') as submit:
            self.assertEqual(self.signed_post(self.event(sender='other')).status_code, 200)
            self.assertEqual(self.signed_post(self.event(phone='other')).status_code, 200)
            submit.assert_not_called()
        self.assertEqual(self.signed_post({'entry': []}).status_code, 200)

    def test_webhook_acknowledges_before_work(self):
        with patch.object(self.web.worker, 'submit') as submit:
            self.assertEqual(self.signed_post(self.event()).status_code, 200)
            submit.assert_called_once_with(self.web.process_message, 'message-1', '15550000000', 'hello')
        # submit was mocked, so release its reservation ourselves.
        self.web.slots.release()

    def deliver(self):
        self.web.slots.acquire()
        self.web.process_message('message-1', '15550000000', 'hello')

    def test_duplicate_delivery_and_retry_use_cached_reply(self):
        with patch.object(self.web, 'handle_message', return_value='Saved') as handle:
            with patch.object(self.web, 'send_reply', side_effect=RuntimeError('network')):
                self.deliver()
            with patch.object(self.web, 'send_reply') as send:
                self.deliver()
                self.deliver()
                send.assert_called_once_with('15550000000', 'Saved')
            handle.assert_called_once()
        self.assertEqual(self.web.reserve('message-1'), (False, None))

    def test_stale_pending_does_not_repeat_unknown_actions(self):
        self.assertEqual(self.web.reserve('crash'), (True, None))
        with self.storage.connection() as db:
            db.execute('UPDATE deliveries SET updated = 0 WHERE id = ?', ('crash',))
        self.assertEqual(self.web.reserve('crash'), (False, None))
        with self.storage.connection() as db:
            self.assertEqual(db.execute('SELECT status FROM deliveries WHERE id = ?', ('crash',)).fetchone()['status'], 'uncertain')


class DistributionTests(unittest.TestCase):
    def test_all_snapshots_are_complete_and_importable(self):
        for number in range(1, 8):
            with self.subTest(module=number), tempfile.TemporaryDirectory() as folder:
                source = ROOT / 'solutions' / f'module_{number}'
                for name in ('main.py', 'config.py', 'agent.py', 'tools.py', 'storage.py', 'whatsapp_server.py', '.env.example', 'requirements.txt', '.gitignore', '.python-version'):
                    self.assertTrue((source / name).is_file(), name)
                    shutil.copy(source / name, folder)
                code = 'import main, config, agent, tools, storage, whatsapp_server; print("ready")'
                result = subprocess.run([sys.executable, '-c', code], cwd=folder, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), 'ready')

    def test_starter_runs_without_keys(self):
        env = dict(os.environ, GEMINI_API_KEY='', GEMINI_MODEL='')
        result = subprocess.run([sys.executable, 'main.py'], cwd=ROOT, input='hello\n/exit\n', text=True, capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Starter running!', result.stdout)
        self.assertIn('Goodbye!', result.stdout)

    def test_sidebar_has_35_unique_lessons_and_existing_support(self):
        sidebar = json.loads((ROOT / 'docs/sidebar.json').read_text())
        lessons = [lesson['id'] for module in sidebar['modules'] for lesson in module['lessons']]
        self.assertEqual(len(lessons), 35)
        self.assertEqual(len(set(lessons)), 35)
        for resource in sidebar['support']:
            self.assertTrue((ROOT / resource['path']).is_file())


if __name__ == '__main__':
    unittest.main()
