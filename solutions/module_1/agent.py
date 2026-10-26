"""Module 1 starter. Build the following pieces as their lessons introduce them.

Module references are in solutions/module_N/agent.py. No API is called yet.
"""


class AgentError(Exception):
    """Display a readable problem without printing secrets."""


# TODO: Lesson 16 — describe the five tools using JSON function schemas.
TOOL_DEFINITIONS = []


def request_model(contents, with_tools=False):
    # TODO: Lessons 6–10 — build the model request, read its response,
    # and turn network/API errors into a helpful AgentError.
    raise NotImplementedError("Lesson 6: connect your model here.")


class Agent:
    def __init__(self):
        # TODO: Lesson 21 — store recent complete turns per user.
        self.history = {}

    def chat(self, message, user_id="terminal"):
        # TODO: Lesson 6 — replace the local reply with a model request.
        # TODO: Lessons 17–20 — execute tools in a bounded MAX_STEPS loop.
        # TODO: Lessons 21–25 — use history and support /reset.
        return "Starter running! In Module 2 you will connect an AI model."
