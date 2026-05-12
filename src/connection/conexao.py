import sqlite3

conn = sqlite3.connect("database/estoque.db")

cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")