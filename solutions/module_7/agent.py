def handle_incoming_whatsapp_message(sender_phone: str, message_text: str) -> str:
    """
    Bridges an incoming WhatsApp text message to your personal AI agent.
    """
    return generate_reply(user_message=message_text, user_id=sender_phone)