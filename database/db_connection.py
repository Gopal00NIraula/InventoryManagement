# database/db_connection.py

import sqlite3
from config import DB_PATH

def get_connection():
    """Create or return a connection to the SQLite database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return None
