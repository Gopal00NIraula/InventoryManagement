import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "inventory.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us dict() rows easily
    return conn
