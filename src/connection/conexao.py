from pathlib import Path
import sqlite3
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parents[2]

DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "estoque.db"

DB_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()