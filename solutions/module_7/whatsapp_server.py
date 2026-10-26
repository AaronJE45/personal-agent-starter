"""Pre-built local WhatsApp transport. See docs/setup_guides.md.

One process, one background worker; acknowledge valid webhooks promptly.
SQLite reserves message IDs across restarts and caches replies before sending.
This is a learning demo, not an always-online or exactly-once delivery system.
"""
import hashlib
import hmac
import logging
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import requests
from flask import Flask, request
import config
import storage
from agent import Agent, AgentError

logger = logging.getLogger(__name__)
assistant = Agent()
worker = ThreadPoolExecutor(max_workers=1)
slots = threading.BoundedSemaphore(20)
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024


def handle_message(text, sender):
    return assistant.chat(text, user_id=sender)


def send_reply(sender, text):
    response = requests.post(
        f"https://graph.facebook.com/{config.META_GRAPH_VERSION}/{config.WHATSAPP_PHONE_NUMBER_ID}/messages",
        headers={"Authorization": f"Bearer {config.WHATSAPP_ACCESS_TOKEN}"},
        json={"messaging_product": "whatsapp", "to": sender, "type": "text",
              "text": {"body": text[:4000]}}, timeout=20,
    )
    # Do not log response bodies, headers, phone numbers, or tokens.
    if response.status_code >= 400:
        raise RuntimeError(f"WhatsApp send failed (HTTP {response.status_code}).")


def reserve(message_id):
    storage.db_init()
    with storage.connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT status, reply, updated FROM deliveries WHERE id = ?", (message_id,)).fetchone()
        if row:
            if row["status"] == "done":
                return False, None
            if row["status"] == "pending":
                if time.time() - row["updated"] > 300:
                    # Crash recovery: do not rerun tools whose outcome is unknown.
                    db.execute("UPDATE deliveries SET status = 'uncertain' WHERE id = ?", (message_id,))
                return False, None
            if row["status"] == "uncertain":
                return False, None
            db.execute("UPDATE deliveries SET status = 'pending', updated = ? WHERE id = ?", (time.time(), message_id))
            return True, row["reply"]
        db.execute("INSERT INTO deliveries (id, status, updated) VALUES (?, 'pending', ?)", (message_id, time.time()))
        return True, None


def process_message(message_id, sender, text):
    cached = None
    reserved = False
    try:
        reserved, cached = reserve(message_id)
        if not reserved:
            return
        if cached is None:
            try:
                cached = handle_message(text, sender)
            except AgentError as error:
                cached = str(error)
            except Exception:
                # A tool could have run; never automatically repeat unknown actions.
                cached = "I could not finish that message. Check saved tasks or notes before retrying."
                logger.warning("Agent processing failed; inspect your configuration and reference solution.")
            with storage.connection() as db:
                db.execute("UPDATE deliveries SET reply = ? WHERE id = ?", (cached, message_id))
        send_reply(sender, cached)
        with storage.connection() as db:
            db.execute("UPDATE deliveries SET status = 'done', updated = ? WHERE id = ?", (time.time(), message_id))
    except Exception:
        if reserved:
            try:
                with storage.connection() as db:
                    db.execute("UPDATE deliveries SET status = 'retry', updated = ? WHERE id = ?", (time.time(), message_id))
            except Exception:
                logger.warning("Could not record delivery state.")
        logger.warning("Delivery failed. See docs/troubleshooting.md. No credentials are logged.")
    finally:
        slots.release()


@app.get("/webhook")
def verify():
    expected = config.WHATSAPP_VERIFY_TOKEN
    supplied = request.args.get("hub.verify_token", "")
    if expected and request.args.get("hub.mode") == "subscribe" and hmac.compare_digest(supplied, expected):
        return request.args.get("hub.challenge", ""), 200, {"Content-Type": "text/plain"}
    return "Verification failed", 403


@app.post("/webhook")
def receive():
    secret = config.WHATSAPP_APP_SECRET
    if not secret:
        return "Configure the app secret first", 503
    expected = "sha256=" + hmac.new(secret.encode(), request.get_data(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(request.headers.get("X-Hub-Signature-256", ""), expected):
        return "Invalid signature", 403
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return "Invalid JSON", 400
    # Ignore delivery-status notifications and non-text messages.
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if value.get("metadata", {}).get("phone_number_id") != config.WHATSAPP_PHONE_NUMBER_ID:
                    continue
                for message in value.get("messages", []):
                    sender, message_id = message.get("from"), message.get("id")
                    text = message.get("text", {}).get("body")
                    if sender != config.WHATSAPP_ALLOWED_SENDER:
                        continue  # Restrict this personal demo to the configured phone.
                    if message.get("type") != "text" or not all(isinstance(x, str) and x for x in (sender, message_id, text)):
                        continue
                    if not slots.acquire(blocking=False):
                        return "Busy; retry later", 503
                    try:
                        worker.submit(process_message, message_id, sender, text)
                    except Exception:
                        slots.release()
                        return "Worker unavailable", 503
    except (AttributeError, TypeError):
        return "Malformed event", 400
    return "OK", 200


def validate_settings():
    names = ["WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_APP_SECRET",
             "WHATSAPP_VERIFY_TOKEN", "WHATSAPP_ALLOWED_SENDER", "META_GRAPH_VERSION"]
    missing = [name for name in names if not getattr(config, name)]
    if missing:
        raise SystemExit("Set these values in .env first: " + ", ".join(missing))
    if not re.fullmatch(r"v\d+\.\d+", config.META_GRAPH_VERSION):
        raise SystemExit("META_GRAPH_VERSION must look like vNN.0; use the version shown by Meta.")
    if not config.WHATSAPP_ALLOWED_SENDER.isdigit():
        raise SystemExit("WHATSAPP_ALLOWED_SENDER must contain country code and digits only, without +.")


if __name__ == "__main__":
    validate_settings()
    # Disable request logs: webhook verification URLs contain your verify token.
    logging.getLogger("werkzeug").disabled = True
    print("Webhook listening at http://127.0.0.1:8000/webhook. Keep this terminal open.")
    app.run(host="127.0.0.1", port=8000, debug=False, use_reloader=False)
