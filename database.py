import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "brew_bytes.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users table for Role-based Login (JWT)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL, -- 'waiter', 'kitchen', 'cashier', 'owner'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Menu items table (Prices stored as integer paise: Rs 140 = 14000 paise)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        price_paise INTEGER NOT NULL,
        category TEXT NOT NULL,
        available INTEGER DEFAULT 1
    )
    """)

    # Orders table (Money stored as integer paise)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        table_number INTEGER NOT NULL,
        customer_name TEXT,
        customer_phone TEXT,
        note TEXT,
        status TEXT NOT NULL DEFAULT 'new', -- 'new', 'cooking', 'ready', 'served', 'cancelled'
        subtotal_paise INTEGER NOT NULL,
        discount_paise INTEGER DEFAULT 0,
        gst_paise INTEGER DEFAULT 0,
        total_paise INTEGER NOT NULL,
        paid_method TEXT, -- 'Cash', 'UPI', 'Card'
        paid_at INTEGER,
        created_at INTEGER NOT NULL
    )
    """)

    # Order items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        item_name TEXT NOT NULL,
        qty INTEGER NOT NULL,
        unit_price_paise INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )
    """)

    # Stock movements ledger (Counter ki jagah har order par stock_movements entry)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movement_type TEXT NOT NULL, -- 'order_deduct', 'restock', 'wastage'
        order_id TEXT,
        ingredient_code TEXT NOT NULL,
        ingredient_name TEXT NOT NULL,
        qty_change REAL NOT NULL, -- negative for deduction, positive for restock
        unit TEXT NOT NULL,
        note TEXT,
        created_at INTEGER NOT NULL
    )
    """)

    # Expenses table (Paise)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount_paise INTEGER NOT NULL,
        created_at INTEGER NOT NULL
    )
    """)

    # Vendors table (Paise)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT NOT NULL,
        amount_paise INTEGER NOT NULL,
        entry_type TEXT NOT NULL, -- 'bill', 'paid'
        created_at INTEGER NOT NULL
    )
    """)

    # Staff table (Salary in paise)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        shift TEXT NOT NULL,
        salary_paise INTEGER NOT NULL
    )
    """)

    # Attendance table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id TEXT NOT NULL,
        date_str TEXT NOT NULL, -- 'YYYY-MM-DD'
        is_present INTEGER NOT NULL,
        UNIQUE(staff_id, date_str)
    )
    """)

    # AI Customer Food Reviews table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        customer_name TEXT,
        customer_phone TEXT NOT NULL,
        items_summary TEXT,
        ai_message TEXT NOT NULL,
        scheduled_at INTEGER NOT NULL,
        dispatched_at INTEGER,
        status TEXT NOT NULL DEFAULT 'scheduled', -- 'scheduled', 'dispatched', 'failed'
        created_at INTEGER NOT NULL
    )
    """)

    # Seed default menu if empty
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    if cursor.fetchone()[0] == 0:
        default_menu = [
            ('Cappuccino', 14000, 'Coffee'),
            ('Cold coffee', 16000, 'Coffee'),
            ('Masala chai', 5000, 'Chai'),
            ('Paneer sandwich', 12000, 'Sandwich'),
            ('Cheese sandwich', 11000, 'Sandwich'),
            ('Cheese toast', 10000, 'Snacks'),
            ('Fries', 11000, 'Snacks'),
            ('Brownie', 9000, 'Dessert')
        ]
        cursor.executemany("INSERT INTO menu_items (name, price_paise, category) VALUES (?, ?, ?)", default_menu)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)

