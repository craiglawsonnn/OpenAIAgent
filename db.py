import sqlite3

def init_db():
    conn = sqlite3.connect("support.db")
    cur = conn.cursor()

    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        status TEXT,
        delivery_date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        summary TEXT
    )
    """)

    # Seed test orders
    cur.execute("INSERT OR IGNORE INTO orders VALUES ('5672', 'Shipped', '2025-06-06')")
    cur.execute("INSERT OR IGNORE INTO orders VALUES ('1234', 'Processing', '2025-06-02')")

    conn.commit()
    conn.close()
