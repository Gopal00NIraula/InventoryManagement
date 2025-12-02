# database/db_setup.py
from database.db_connection import get_connection

BASE_USERS_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('manager','employee')) DEFAULT 'employee',
    manager_id INTEGER NULL,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    business_name TEXT,
    created_at TEXT,
    FOREIGN KEY(manager_id) REFERENCES users(id)
);
"""

BASE_ITEMS_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    price REAL DEFAULT 0.0
);
"""

def _existing_cols(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}  # set of column names

def _migrate_users(conn):
    cur = conn.cursor()
    # ensure table exists
    cur.execute(BASE_USERS_SQL)

    cols = _existing_cols(cur, "users")

    # simple columns that can be added with constant defaults or NULL
    simple_alters = {
        "email":         "ALTER TABLE users ADD COLUMN email TEXT",
        "role":          "ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'employee'",
        "manager_id":    "ALTER TABLE users ADD COLUMN manager_id INTEGER NULL",
        "first_name":    "ALTER TABLE users ADD COLUMN first_name TEXT",
        "last_name":     "ALTER TABLE users ADD COLUMN last_name TEXT",
        "phone":         "ALTER TABLE users ADD COLUMN phone TEXT",
        "business_name": "ALTER TABLE users ADD COLUMN business_name TEXT",
    }
    for col, sql in simple_alters.items():
        if col not in cols:
            cur.execute(sql)

    # created_at needs special handling (no non-constant defaults allowed in ALTER)
    if "created_at" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
        # backfill existing rows
        cur.execute("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL")

    # optional unique index on email
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_users_email ON users(email)")
    conn.commit()

def _migrate_items(conn):
    cur = conn.cursor()
    # ensure table exists
    cur.execute(BASE_ITEMS_SQL)
    
    cols = _existing_cols(cur, "items")
    
    # Add price column if it doesn't exist (migrate from location to price)
    if "price" not in cols:
        cur.execute("ALTER TABLE items ADD COLUMN price REAL DEFAULT 0.0")
        print("[DB] Added 'price' column to items table")
    
    conn.commit()

def setup_database():
    conn = get_connection()
    cur = conn.cursor()

    # create tables if missing
    cur.execute(BASE_USERS_SQL)
    cur.execute(BASE_ITEMS_SQL)
    conn.commit()

    # migrate users table to include any missing columns
    _migrate_users(conn)
    
    # migrate items table to include price column
    _migrate_items(conn)

    conn.close()
    print("[DB] Setup/migration complete.")
    
if __name__ == "__main__":
    setup_database()
