"""An explicit Gemini generateContent loop, with no agent framework.

The raw model content is passed back unchanged: this preserves tool-call IDs
and provider thought signatures. History is grouped by complete user turns.
"""
from copy import deepcopy
from urllib.parse import quote
import requests
import config
from tools import TOOL_FUNCTIONS


class AgentError(Exception):
    """A readable error safe to display without exposing tokens or payloads."""


def _tool(name, description, properties, required):
    return {"name": name, "description": description, "parameters": {
        "type": "OBJECT", "properties": properties, "required": required}}


TOOL_DEFINITIONS = [
    _tool("add_task", "Save a task.", {"title": {"type": "STRING"}}, ["title"]),
    _tool("list_tasks", "List the user's tasks.", {}, []),
    _tool("complete_task", "Complete a task by its numeric ID.", {"task_id": {"type": "INTEGER"}}, ["task_id"]),
    _tool("save_note", "Save a note.", {"text": {"type": "STRING"}}, ["text"]),
    _tool("search_notes", "Find saved notes by a keyword or phrase.", {"query": {"type": "STRING"}}, ["query"]),
]


def request_model(contents, with_tools=True):
    if not config.GEMINI_API_KEY or not config.GEMINI_MODEL:
        raise AgentError("Set GEMINI_API_KEY and GEMINI_MODEL in .env. See docs/free_tier_limits.md.")
    body = {
        "systemInstruction": {"parts": [{"text": config.SYSTEM_INSTRUCTION}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 1024},
    }
    if with_tools:
        body["tools"] = [{"functionDeclarations": TOOL_DEFINITIONS}]
    model = quote(config.GEMINI_MODEL, safe="")
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": config.GEMINI_API_KEY}, json=body, timeout=45,
        )
    except requests.RequestException:
        raise AgentError("Cannot reach the model. Check your connection and retry.") from None
    if response.status_code == 429:
        raise AgentError("Model quota reached. Wait and check your AI Studio limits; do not enable billing.")
    if response.status_code >= 400:
        raise AgentError(f"Model request failed (HTTP {response.status_code}). Check key, model access and docs/troubleshooting.md.")
    try:
        content = response.json()["candidates"][0]["content"]
        if not isinstance(content.get("parts"), list):
            raise ValueError
        return content
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        raise AgentError("The model returned no usable answer. Try a different message.") from None


class Agent:
    def __init__(self):
        self.history = {}  # user_id -> list of complete turns (Module 5)

    def chat(self, message, user_id="terminal"):
        if not isinstance(message, str) or not message.strip():
            return "Please enter a message."
        if len(message) > 4000:
            return "Please keep your message under 4,000 characters."
        if message.strip().lower() == "/reset":
            self.history.pop(user_id, None)
            return "Conversation history cleared. Saved notes and tasks are unchanged."
        turns = []  # Conversation memory is introduced in Module 5.
        contents = [deepcopy(item) for turn in turns for item in turn]
        start = len(contents)
        contents.append({"role": "user", "parts": [{"text": message.strip()}]})
        for _ in range(config.MAX_STEPS):
            content = request_model(contents)
            contents.append(content)
            calls = [part["functionCall"] for part in content["parts"] if "functionCall" in part]
            if not calls:
                answer = "\n".join(part["text"] for part in content["parts"] if "text" in part and not part.get("thought"))
                if not answer:
                    raise AgentError("No text answer was returned. Please try again.")
                # Module 5: retain this complete turn in self.history.
                return answer
            results = []
            for call in calls:
                name, args = call.get("name", ""), call.get("args", {})
                try:
                    if name not in TOOL_FUNCTIONS or not isinstance(args, dict) or "user_id" in args:
                        raise ValueError("Unknown tool or invalid arguments.")
                    # user_id comes from our app, NEVER from model-supplied arguments.
                    output = TOOL_FUNCTIONS[name](**args, user_id=user_id)
                except (TypeError, ValueError, NotImplementedError) as error:
                    output = {"error": str(error)}
                result = {"name": name, "response": {"result": output}}
                if "id" in call:
                    result["id"] = call["id"]
                results.append({"functionResponse": result})
            contents.append({"role": "user", "parts": results})
        # Some tools may already have succeeded; do not silently repeat the request.
        return "I reached my step limit. Some actions may have completed; list your tasks or notes before retrying."
