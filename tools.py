"""Module 3 exercises. Compare with solutions/module_3/tools.py if stuck."""

def add_task(title, *, user_id="terminal"):
    # TODO: Lesson 12 — save a task in a user-specific in-memory list.
    raise NotImplementedError("Lesson 12: implement add_task.")


def list_tasks(*, user_id="terminal"):
    # TODO: Lesson 12 — return this user's tasks.
    raise NotImplementedError("Lesson 12: implement list_tasks.")


def complete_task(task_id, *, user_id="terminal"):
    # TODO: Lesson 13 — mark a matching task complete.
    raise NotImplementedError("Lesson 13: implement complete_task.")


def save_note(text, *, user_id="terminal"):
    # TODO: Lesson 14 — save a note for this user.
    raise NotImplementedError("Lesson 14: implement save_note.")


def search_notes(query, *, user_id="terminal"):
    # TODO: Lesson 14 — return notes containing the query.
    # TODO: Lesson 15 — reject empty inputs in tools.
    raise NotImplementedError("Lesson 14: implement search_notes.")


TOOL_FUNCTIONS = {
    "add_task": add_task, "list_tasks": list_tasks,
    "complete_task": complete_task, "save_note": save_note,
    "search_notes": search_notes,
}
