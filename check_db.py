import sqlite3
conn = sqlite3.connect(r"C:\Downloads\app\experion.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS users;")
cur.execute("DROP TABLE IF EXISTS submissions;")

cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    project_title TEXT NOT NULL,
    description TEXT NOT NULL
);
""")

conn.commit()
conn.close()
