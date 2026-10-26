# whatsapp_server.py
import os
import hmac
import hashlib
import requests
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from agent import generate_reply

load_dotenv()

app = FastAPI(title="Personal AI Agent WhatsApp Webhook")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "").strip()
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "metana_verify_token_123").strip()
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "").strip()

# Set of processed WhatsApp message IDs to prevent duplicate replies on webhook retries
PROCESSED_MESSAGE_IDS: set[str] = set()


def verify_webhook_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Validates X-Hub-Signature-256 if WHATSAPP_APP_SECRET is configured."""
    if not WHATSAPP_APP_SECRET:
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        WHATSAPP_APP_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    received = signature_header.split("sha256=", 1)[1]
    return hmac.compare_digest(expected, received)


def send_whatsapp_reply(recipient_phone: str, reply_text: str) -> dict:
    """Sends a text reply back to the user via the official WhatsApp Cloud API."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print(f"[WhatsApp Dry-Run Reply to {recipient_phone}]: {reply_text}")
        return {"status": "dry_run", "to": recipient_phone, "text": reply_text}

    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": reply_text},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=20)
    return {"status": "sent", "http_status": resp.status_code}


def handle_incoming_whatsapp_message(sender_phone: str, message_text: str) -> str:
    """
    Bridges an incoming WhatsApp text message to your personal AI agent.
    """
    # TODO: Lesson 29 - Pass message_text and user_id=sender_phone to generate_reply()
    # and return the agent's reply string!
    return f"Echo from starter webhook (Connect generate_reply in Lesson 29): {message_text}"


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    """Handles Meta's GET /webhook verification challenge."""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("✅ Webhook verified successfully with Meta!")
        return PlainTextResponse(content=hub_challenge or "", status_code=200)
    raise HTTPException(status_code=403, detail="Webhook verification failed: token mismatch.")


@app.post("/webhook")
async def receive_whatsapp_webhook(request: Request):
    """Receives incoming WhatsApp messages, deduplicates them, and replies via the agent."""
    raw_body = await request.body()
    sig_header = request.headers.get("X-Hub-Signature-256")
    if not verify_webhook_signature(raw_body, sig_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature.")

    payload = await request.json()
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    msg_id = msg.get("id")
                    if msg_id and msg_id in PROCESSED_MESSAGE_IDS:
                        continue
                    if msg_id:
                        PROCESSED_MESSAGE_IDS.add(msg_id)

                    if msg.get("type") == "text":
                        sender_phone = msg.get("from", "whatsapp_user")
                        message_text = msg.get("text", {}).get("body", "").strip()
                        if message_text:
                            print(f"📩 [WhatsApp Incoming from {sender_phone}]: {message_text}")
                            reply_text = handle_incoming_whatsapp_message(sender_phone, message_text)
                            print(f"📤 [Agent Reply to {sender_phone}]: {reply_text}")
                            send_whatsapp_reply(sender_phone, reply_text)
    except Exception as exc:
        print(f"⚠️ Error processing webhook payload: {exc}")

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting WhatsApp Webhook Server on http://localhost:8000 ...")
    uvicorn.run(app, host="0.0.0.0", port=8000)