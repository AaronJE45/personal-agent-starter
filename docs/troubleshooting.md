# Troubleshooting without an instructor

Use the symptom table, compare the expected result, then consult the matching
module snapshot. There is no personalised support or automated code grading.

| Symptom | What to try |
| --- | --- |
| `python` or `py` is not found | Install Python, reopen the terminal, use your OS's commands in setup_guides.md. |
| `No module named flask`, `requests`, or `dotenv` | Use the virtual environment's Python and reinstall `requirements.txt`. |
| PowerShell refuses activation | Run `.\.venv\Scripts\python.exe main.py` directly. |
| Can't find `main.py` | Open the project folder, not its parent or a solution directory. |
| Still seeing the starter reply | Module 1 deliberately has no AI. Complete Module 2 or use its reference snapshot. |
| `NotImplementedError` | This is a marked tool exercise. See the lesson number and Module 3 solution. |
| Missing model configuration | Put both values in this project's `.env`, not `.env.txt`; restart. |
| Model HTTP 400 | Check the exact model ID and compare the request with the same-module reference. |
| Model HTTP 401/403 | Check API key validity, model permission, region and account eligibility. |
| Model HTTP 404 | Choose an available free-tier model; do not prefix its ID with `models/`. |
| Model quota reached / HTTP 429 | Stop retrying, inspect AI Studio's actual quotas, and wait for the appropriate reset. |
| Connection timeout | Check internet access and provider status; avoid rapid retries. |
| Tasks vanish on restart | Before Module 5 that is expected. Later check `USE_DATABASE = True` and `data/`. |
| Notes search finds nothing | This course uses exact substring matching, not semantic search. Try a word from the note. |
| Another program's data is missing | Terminal and WhatsApp use different user IDs; their notes/tasks are intentionally separate. |
| Agent hits its step limit | Some tools may have run. List tasks/notes before requesting the action again. |
| Port 8000 is busy | Stop your previous server; do not start multiple copies. |
| Webhook GET verification fails | Match your chosen verify token, include `/webhook`, and check the current HTTPS tunnel URL. |
| Webhook POST returns 403 | Verify App Secret belongs to the same Meta app. Unsigned manual POSTs are intentionally rejected. |
| Webhook connects but ignores my message | Match the phone-number ID, allowed sender (digits only), recipient verification and messages subscription. |
| WhatsApp reply stays “Webhook connected!” | Complete the `TODO: Lesson 29` hook, save the file, restart the server. |
| WhatsApp send fails | Check the temporary token's expiry in Meta, recipient setup and Graph version. Restart after editing `.env`. |
| Tunnel worked yesterday | Quick tunnel URLs change. Restart it and update Meta's callback. |
| Laptop was asleep | Start server/tunnel again and send a new message; delivery during downtime is not guaranteed. |
| Duplicate actions/replies | Keep one server process. Provider retries are deduplicated by message ID; a new message is a new request. |
| A crashed message never replies | Do not delete delivery records blindly. Check notes/tasks first, then send a new message. See delivery limitations below. |

## How to Restart Your Agent

1. Open the original project folder. Do not copy `.env.example` over your existing `.env`.
2. macOS/Linux: `source .venv/bin/activate`. Windows: use `.\.venv\Scripts\python.exe`.
3. For terminal chat: `python main.py`.
4. For WhatsApp: refresh an expired Meta token in `.env`, then `python whatsapp_server.py`.
5. In a second terminal: `cloudflared tunnel --url http://127.0.0.1:8000`.
6. Update Meta's callback to the new HTTPS URL plus `/webhook`; verify again if needed.
7. Send a new message from your configured recipient phone.

Do not recreate the virtual environment, reset your database, or reclone the repo
on every restart. Conversation history is held in memory and resets when the
program stops. From Module 5, notes and tasks remain in `data/agent.sqlite3`.

## Recover a module

Follow [solutions/README.md](../solutions/README.md). Save a commit first, copy
only the six Python files, and keep `.env` and `data/`. This restores the reference
behaviour; reapply your assistant's name/personality afterwards.

## Delivery limitations

The server acknowledges events and processes them on a single background worker.
It stores message IDs and cached replies in SQLite. Repeated deliveries do not
rerun completed tools. If sending fails, a later delivery can resend the cached
reply, without running the agent again. There is no automatic retry scheduler:
if no redelivery happens, the reply can remain unsent.

A crash during a tool action can leave its outcome uncertain. Such a message is
not automatically re-executed. Also, a timeout after Meta accepted a send can
produce a duplicate reply on retry. Exactly-once messaging is not guaranteed.
This single-process local demo does not provide production durability or uptime.
Delivery metadata is kept in your private local database; delete local demo data
only when you intentionally want to erase it, with the server stopped.
