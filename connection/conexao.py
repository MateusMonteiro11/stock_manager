from pathlib import Path
import os
import sqlite3
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parents[2]

configured_db_path = os.getenv("MYSTOCK_SQLITE_DB_PATH")
DB_PATH = (
    Path(configured_db_path).expanduser().resolve()
    if configured_db_path
    else BASE_DIR / "database" / "estoque.db"
)
DB_DIR = DB_PATH.parent

DB_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()
