# agent.py
from config import AGENT_NAME, SYSTEM_INSTRUCTION, call_model_api

def send_first_request() -> str:
    prompt = f"Hello! Introduce yourself as {AGENT_NAME} in one short sentence."
    print(f"[Request Sent]  : {prompt}")

    # TODO: Lesson 6 - Uncomment the call_model_api call below to send your first request
    # response_text = call_model_api(
    #     system_instruction="You are a friendly personal assistant.",
    #     user_message=prompt
    # )
    response_text = "Uncomment call_model_api in agent.py for Lesson 6!"

    print(f"[Model Response]: {response_text}")
    return response_text

# TODO: Lesson 7 - Add generate_reply(user_message)
# TODO: Lesson 16 - Add TOOL_SCHEMAS
# TODO: Lesson 18 - Add AVAILABLE_TOOLS and execute_tool_call()
# TODO: Lesson 20 - Upgrade generate_reply() with MAX_STEPS agent loop
# TODO: Lesson 21 & 25 - Add CONVERSATION_HISTORY, MAX_HISTORY_MESSAGES, and reset_conversation()