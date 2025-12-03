from database.db_connection import get_connection

BASE_USERS_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('ADMIN','STAFF','VIEWER')) DEFAULT 'STAFF',
    manager_id INTEGER NULL,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    business_name TEXT,
    created_at TEXT,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY(manager_id) REFERENCES users(id)
);
"""

BASE_ITEMS_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    price REAL DEFAULT 0.0,
    min_stock_level INTEGER DEFAULT 10,
    reorder_point INTEGER DEFAULT 20,
    barcode TEXT
);
"""

BASE_SUPPLIERS_SQL = """
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

BASE_CUSTOMERS_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

BASE_PURCHASE_ORDERS_SQL = """
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    supplier_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'COMPLETED', 'CANCELLED')) DEFAULT 'PENDING',
    notes TEXT,
    created_by INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    FOREIGN KEY(supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY(item_id) REFERENCES items(id),
    FOREIGN KEY(created_by) REFERENCES users(id)
);
"""

BASE_SALES_ORDERS_SQL = """
CREATE TABLE IF NOT EXISTS sales_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'COMPLETED', 'CANCELLED')) DEFAULT 'PENDING',
    notes TEXT,
    created_by INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(item_id) REFERENCES items(id),
    FOREIGN KEY(created_by) REFERENCES users(id)
);
"""

BASE_STOCK_ALERTS_SQL = """
CREATE TABLE IF NOT EXISTS stock_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL CHECK(alert_type IN ('LOW_STOCK', 'OUT_OF_STOCK', 'REORDER')),
    message TEXT NOT NULL,
    quantity_at_alert INTEGER NOT NULL,
    is_resolved INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT,
    FOREIGN KEY(item_id) REFERENCES items(id)
);
"""

BASE_AUDIT_LOGS_SQL = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id INTEGER,
    details TEXT,
    ip_address TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id)
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

    # Add is_active column if it doesn't exist
    if "is_active" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
        cur.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")
    
    # optional unique index on email
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_users_email ON users(email)")
    conn.commit()

def _migrate_roles(conn):
    """Migrate old manager/employee roles to new ADMIN/STAFF/VIEWER system"""
    cur = conn.cursor()
    
    # Check if any users have old role values
    cur.execute("SELECT COUNT(*) FROM users WHERE role IN ('manager', 'employee')")
    old_role_count = cur.fetchone()[0]
    
    if old_role_count > 0:
        print(f"[DB] Migrating {old_role_count} users from old role system...")
        # Convert manager -> ADMIN, employee -> STAFF
        cur.execute("UPDATE users SET role = 'ADMIN' WHERE role = 'manager'")
        cur.execute("UPDATE users SET role = 'STAFF' WHERE role = 'employee'")
        conn.commit()
        print("[DB] Role migration complete: manager->ADMIN, employee->STAFF")
    
    # Ensure all users have valid roles
    cur.execute("UPDATE users SET role = 'STAFF' WHERE role NOT IN ('ADMIN', 'STAFF', 'VIEWER')")
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
    
    # Add stock alert columns if they don't exist
    if "min_stock_level" not in cols:
        cur.execute("ALTER TABLE items ADD COLUMN min_stock_level INTEGER DEFAULT 10")
        print("[DB] Added 'min_stock_level' column to items table")
    
    if "reorder_point" not in cols:
        cur.execute("ALTER TABLE items ADD COLUMN reorder_point INTEGER DEFAULT 20")
        print("[DB] Added 'reorder_point' column to items table")
    
    # Add barcode column if it doesn't exist (without UNIQUE constraint initially)
    if "barcode" not in cols:
        cur.execute("ALTER TABLE items ADD COLUMN barcode TEXT")
        print("[DB] Added 'barcode' column to items table")
    
    conn.commit()

def setup_database():
    conn = get_connection()
    cur = conn.cursor()

    # create tables if missing
    cur.execute(BASE_USERS_SQL)
    cur.execute(BASE_ITEMS_SQL)
    cur.execute(BASE_SUPPLIERS_SQL)
    cur.execute(BASE_CUSTOMERS_SQL)
    cur.execute(BASE_PURCHASE_ORDERS_SQL)
    cur.execute(BASE_SALES_ORDERS_SQL)
    cur.execute(BASE_STOCK_ALERTS_SQL)
    cur.execute(BASE_AUDIT_LOGS_SQL)
    conn.commit()

    # migrate users table to include any missing columns
    _migrate_users(conn)
    
    # migrate items table to include price column
    _migrate_items(conn)
    
    # migrate old roles to new role system
    _migrate_roles(conn)

    conn.close()
    print("[DB] Setup/migration complete.")
    
if __name__ == "__main__":
    setup_database()
