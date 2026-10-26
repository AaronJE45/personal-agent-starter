"""Run with: python main.py. No key is needed for the Module 1 starter."""
from agent import Agent, AgentError
from config import AGENT_NAME


def main():
    assistant = Agent()
    print(f"{AGENT_NAME} is ready. Type /exit to leave or /reset to clear chat history.")
    while True:  # Lesson 9: a loop lets us send more than one message.
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if message.lower() == "/exit":
            print("Goodbye!")
            break
        if not message:
            continue
        try:
            print(f"{AGENT_NAME}: {assistant.chat(message, user_id='terminal')}")
        except AgentError as error:
            print(f"Help: {error}")


if __name__ == "__main__":
    main()
