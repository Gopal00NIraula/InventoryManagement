# database/db_setup.py

from database.db_connection import get_connection

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    # --- Create Users Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'staff'
    )
    """)

    # --- Create Inventory Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        sku TEXT,
        category TEXT,
        quantity INTEGER DEFAULT 0,
        price REAL DEFAULT 0.0,
        threshold INTEGER DEFAULT 5
    )
    """)

    conn.commit()
    conn.close()
    print("[DB] Tables created successfully.")

if __name__ == "__main__":
    setup_database()
