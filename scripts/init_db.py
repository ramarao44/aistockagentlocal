import sqlite3
from pathlib import Path

DB_PATH = Path("data/agent.db")
SCHEMA_PATH = Path("data/schema.sql")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = f.read()
        conn.executescript(schema)
        conn.commit()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
