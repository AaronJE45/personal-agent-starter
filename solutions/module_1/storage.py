"""Pre-built SQLite helpers. Module 5 connects these to tools.py.

Every operation filters by user_id. Connections are short-lived and queries
are parameterised. This database is private local data: never commit it.
"""
import sqlite3
from contextlib import contextmanager
import config


@contextmanager
def connection():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(config.DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()


def db_init():
    with connection() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY, user_id TEXT NOT NULL,
                title TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, text TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS deliveries (
                id TEXT PRIMARY KEY, status TEXT NOT NULL,
                reply TEXT, updated REAL NOT NULL);
        """)


def db_add_task(user_id, title):
    db_init()
    with connection() as db:
        cursor = db.execute("INSERT INTO tasks (user_id, title) VALUES (?, ?)", (user_id, title))
        return {"id": cursor.lastrowid, "title": title, "completed": False}


def db_list_tasks(user_id):
    db_init()
    with connection() as db:
        rows = db.execute("SELECT id, title, completed FROM tasks WHERE user_id = ? ORDER BY id", (user_id,))
        return [dict(row, completed=bool(row["completed"])) for row in rows]


def db_complete_task(user_id, task_id):
    db_init()
    with connection() as db:
        result = db.execute("UPDATE tasks SET completed = 1 WHERE user_id = ? AND id = ?", (user_id, task_id))
        return {"completed": bool(result.rowcount), "id": task_id}


def db_save_note(user_id, text):
    db_init()
    with connection() as db:
        cursor = db.execute("INSERT INTO notes (user_id, text) VALUES (?, ?)", (user_id, text))
        return {"id": cursor.lastrowid, "text": text}


def db_search_notes(user_id, query):
    db_init()
    with connection() as db:
        rows = db.execute("SELECT id, text FROM notes WHERE user_id = ? ORDER BY id", (user_id,))
        # Plain substring matching: %, _ and SQL characters are just text.
        return [dict(row) for row in rows if query.casefold() in row["text"].casefold()]
