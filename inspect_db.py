# inspect_db.py
import sqlite3, os
p = os.path.join(os.path.dirname(__file__), "inventory.db")
print("DB:", os.path.abspath(p))
con = sqlite3.connect(p); con.row_factory = sqlite3.Row
cur = con.cursor()
print("Tables:", [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")])
for t in ("users","items"):
    print(f"\n-- {t} schema --")
    for (sql,) in con.execute("SELECT sql FROM sqlite_master WHERE name=?", (t,)):
        print(sql)
    print(f"\nSample {t}:")
    for row in cur.execute(f"SELECT * FROM {t} LIMIT 10"):
        print(dict(row))
con.close()
