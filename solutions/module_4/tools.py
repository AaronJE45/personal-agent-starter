"""Lessons 11–15: small tools; Lesson 23: switch from memory to SQLite."""
import config
import storage

_tasks = {}
_notes = {}


def _text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Enter some text first.")
    if len(value) > 2000:
        raise ValueError("Please keep text under 2,000 characters.")
    return value.strip()


def add_task(title, *, user_id="terminal"):
    title = _text(title)
    if config.USE_DATABASE:
        return storage.db_add_task(user_id, title)
    tasks = _tasks.setdefault(user_id, [])
    task = {"id": len(tasks) + 1, "title": title, "completed": False}
    tasks.append(task)
    return dict(task)


def list_tasks(*, user_id="terminal"):
    if config.USE_DATABASE:
        return storage.db_list_tasks(user_id)
    return [dict(task) for task in _tasks.get(user_id, [])]


def complete_task(task_id, *, user_id="terminal"):
    if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
        raise ValueError("task_id must be a positive whole number.")
    if config.USE_DATABASE:
        return storage.db_complete_task(user_id, task_id)
    for task in _tasks.get(user_id, []):
        if task["id"] == task_id:
            task["completed"] = True
            return {"completed": True, "id": task_id}
    return {"completed": False, "id": task_id}


def save_note(text, *, user_id="terminal"):
    text = _text(text)
    if config.USE_DATABASE:
        return storage.db_save_note(user_id, text)
    notes = _notes.setdefault(user_id, [])
    note = {"id": len(notes) + 1, "text": text}
    notes.append(note)
    return dict(note)


def search_notes(query, *, user_id="terminal"):
    query = _text(query)
    if config.USE_DATABASE:
        return storage.db_search_notes(user_id, query)
    return [dict(note) for note in _notes.get(user_id, []) if query.casefold() in note["text"].casefold()]


TOOL_FUNCTIONS = {
    "add_task": add_task, "list_tasks": list_tasks,
    "complete_task": complete_task, "save_note": save_note,
    "search_notes": search_notes,
}
