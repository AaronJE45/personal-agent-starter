# tools.py
from datetime import datetime

# In-memory storage for Modules 3 & 4 (upgraded to SQLite in Module 5)
TASKS = []
NOTES = []

def get_current_time() -> dict:
    """Returns the current local date and time as a structured dictionary."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "status": "success",
        "current_time": now
    }

# TODO: Lesson 12 - Implement add_task(title: str) and list_tasks()
# TODO: Lesson 13 - Implement complete_task(task_id: int)
# TODO: Lesson 14 - Implement save_note(content: str) and search_notes(query: str = "")
# TODO: Lesson 15 - Add input validation to all tool functions
# TODO: Lesson 23 & 24 - Connect tools to SQLite helpers in storage.py with user_id isolation