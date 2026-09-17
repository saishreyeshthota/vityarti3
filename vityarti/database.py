import sqlite3
import os
import shutil
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Detect if running in Vercel or serverless read-only environment
IS_SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "canteen.db")

def get_active_db_path(custom_path=None):
    if custom_path:
        return custom_path
    if IS_SERVERLESS:
        tmp_db = "/tmp/canteen.db"
        bundled_db = DEFAULT_DB_PATH
        if not os.path.exists(tmp_db) and os.path.exists(bundled_db):
            try:
                shutil.copy2(bundled_db, tmp_db)
            except Exception:
                pass
        return tmp_db
    return DEFAULT_DB_PATH


FALLBACK_MENU_ITEMS = [
    {
        "id": 1,
        "name": "Artisan Veggie Burger Combo",
        "category": "Snacks",
        "description": "Char-grilled herb patty, melted cheddar, crisp lettuce, farm tomato on a brioche bun with golden fries & dip.",
        "price": 120.00,
        "is_available": 1,
        "stock_quantity": 40,
        "dietary_type": "veg",
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 12,
        "calories": 540,
        "rating": 4.9
    },
    {
        "id": 2,
        "name": "Royal Mysore Masala Dosa",
        "category": "Breakfast",
        "description": "Crispy golden crepe smeared with spicy red chutney, stuffed with spiced potato mash, served with coconut chutney & sambar.",
        "price": 85.00,
        "is_available": 1,
        "stock_quantity": 60,
        "dietary_type": "veg",
        "image_url": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 8,
        "calories": 380,
        "rating": 4.9
    },
    {
        "id": 3,
        "name": "Signature Caramel Iced Macchiato",
        "category": "Beverages",
        "description": "Velvety cold-brew espresso with chilled whole milk, rich vanilla syrup, and decadent golden caramel swirl.",
        "price": 95.00,
        "is_available": 1,
        "stock_quantity": 75,
        "dietary_type": "veg",
        "image_url": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 4,
        "calories": 210,
        "rating": 4.8
    },
    {
        "id": 4,
        "name": "Mediterranean Nourish Bowl",
        "category": "Healthy",
        "description": "Fluffy quinoa, creamy avocado, crisp chickpeas, heirloom tomatoes, English cucumber ribbons, and tahini drizzle.",
        "price": 140.00,
        "is_available": 1,
        "stock_quantity": 35,
        "dietary_type": "vegan",
        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 10,
        "calories": 390,
        "rating": 4.7
    },
    {
        "id": 5,
        "name": "Steaming Idli Sambar Platter (3 pcs)",
        "category": "Breakfast",
        "description": "Melt-in-mouth fermented steamed rice-lentil cakes immersed in hot aromatic drumstick sambar and fresh mint chutney.",
        "price": 55.00,
        "is_available": 1,
        "stock_quantity": 50,
        "dietary_type": "veg",
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 5,
        "calories": 260,
        "rating": 4.6
    },
    {
        "id": 6,
        "name": "Paneer Butter Masala Thali",
        "category": "Lunch",
        "description": "Tender cottage cheese cubes simmered in rich buttery tomato cashew gravy, served with 2 butter naans, jeera rice, and salad.",
        "price": 160.00,
        "is_available": 1,
        "stock_quantity": 45,
        "dietary_type": "veg",
        "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 15,
        "calories": 680,
        "rating": 4.9
    },
    {
        "id": 7,
        "name": "Schezwan Wok Hakka Noodles",
        "category": "Lunch",
        "description": "Wok-tossed noodles with shredded bell peppers, cabbage, spring onion, and house spicy garlic Schezwan sauce.",
        "price": 110.00,
        "is_available": 1,
        "stock_quantity": 50,
        "dietary_type": "veg",
        "image_url": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 10,
        "calories": 480,
        "rating": 4.6
    },
    {
        "id": 8,
        "name": "Classic Bombay Vada Pav (2 pcs)",
        "category": "Snacks",
        "description": "Spiced potato fritters encased in fluffy pav buns, layered with fiery garlic chutney and fried green chillies.",
        "price": 45.00,
        "is_available": 1,
        "stock_quantity": 80,
        "dietary_type": "veg",
        "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 5,
        "calories": 320,
        "rating": 4.8
    },
    {
        "id": 9,
        "name": "Spiced Kulhad Adrak Chai",
        "category": "Beverages",
        "description": "Slow-brewed Assam tea leaves infused with crushed fresh ginger, green cardamom, and served steaming in an earthen kulhad.",
        "price": 25.00,
        "is_available": 1,
        "stock_quantity": 120,
        "dietary_type": "veg",
        "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 3,
        "calories": 90,
        "rating": 4.9
    },
    {
        "id": 10,
        "name": "Fresh Alphonso Mango Smoothie",
        "category": "Beverages",
        "description": "Thick blend of real Alphonso mango pulp, chilled Greek yogurt, honey, and crushed pistachio garnish.",
        "price": 75.00,
        "is_available": 1,
        "stock_quantity": 40,
        "dietary_type": "veg",
        "image_url": "https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 5,
        "calories": 230,
        "rating": 4.8
    },
    {
        "id": 11,
        "name": "Peri-Peri Golden Crinkle Fries",
        "category": "Snacks",
        "description": "Crispy golden crinkle-cut potato fries dusted with tangy, spicy African peri-peri seasoning and garlic mayo dip.",
        "price": 65.00,
        "is_available": 1,
        "stock_quantity": 60,
        "dietary_type": "vegan",
        "image_url": "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 6,
        "calories": 310,
        "rating": 4.7
    },
    {
        "id": 12,
        "name": "Protein Sprouted Chickpea Salad",
        "category": "Healthy",
        "description": "Sprouted organic chickpeas, pomegranate pearls, diced cucumber, tomatoes, tossed with extra virgin olive oil & chaat masala.",
        "price": 90.00,
        "is_available": 1,
        "stock_quantity": 30,
        "dietary_type": "vegan",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop&q=80",
        "prep_time_minutes": 6,
        "calories": 220,
        "rating": 4.8
    }
]


def get_db_connection(db_path=None):
    """Returns a SQLite database connection with row factory set to sqlite3.Row."""
    path = get_active_db_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None):
    """Initializes the database schema and populates seed data if empty."""
    path = get_active_db_path(db_path)
    conn = get_db_connection(path)
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'faculty', 'staff', 'admin')),
        wallet_balance REAL DEFAULT 0.0,
        roll_no TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # 2. Menu items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        is_available INTEGER DEFAULT 1,
        stock_quantity INTEGER DEFAULT 50,
        dietary_type TEXT DEFAULT 'veg' CHECK(dietary_type IN ('veg', 'non-veg', 'vegan')),
        image_url TEXT,
        prep_time_minutes INTEGER DEFAULT 10,
        calories INTEGER DEFAULT 300,
        rating REAL DEFAULT 4.8,
        created_at TEXT NOT NULL
    );
    """)

    # 3. Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        token_number TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        discount_amount REAL DEFAULT 0.0,
        final_amount REAL NOT NULL,
        payment_method TEXT DEFAULT 'wallet',
        payment_status TEXT DEFAULT 'paid',
        order_status TEXT DEFAULT 'pending' CHECK(order_status IN ('pending', 'preparing', 'ready', 'completed', 'cancelled')),
        special_instructions TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """)

    # 4. Order items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
        FOREIGN KEY (item_id) REFERENCES menu_items (id)
    );
    """)

    # 5. Wallet transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallet_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL CHECK(transaction_type IN ('credit', 'debit')),
        reference TEXT,
        balance_after REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """)

    # 6. Audit logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL
    );
    """)

    # Indexes for high performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_menu_category ON menu_items(category);")

    conn.commit()

    # Seed data if no users or menu items exist
    cursor.execute("SELECT COUNT(*) as cnt FROM users")
    if cursor.fetchone()["cnt"] == 0:
        seed_data(conn)
    else:
        cursor.execute("SELECT COUNT(*) as cnt FROM menu_items")
        if cursor.fetchone()["cnt"] == 0:
            seed_data(conn)

    conn.close()


def seed_data(conn):
    """Seeds initial users, rich menu items, sample orders and wallet balances."""
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    hashed_pwd = generate_password_hash("password123")

    # Seed Users
    users = [
        ("aarav", "student@campus.edu", hashed_pwd, "Aarav Sharma", "student", 450.00, "21BCE1042", now_str),
        ("priya", "faculty@campus.edu", hashed_pwd, "Dr. Priya Raman", "faculty", 1200.00, "FAC802", now_str),
        ("ramesh", "staff@canteen.edu", hashed_pwd, "Ramesh Chef", "staff", 0.00, "STF101", now_str),
        ("vikram", "admin@campus.edu", hashed_pwd, "Vikram Malhotra", "admin", 0.00, "ADM001", now_str),
    ]
    cursor.executemany("""
    INSERT INTO users (username, email, password_hash, full_name, role, wallet_balance, roll_no, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, users)

    # Initial wallet transactions for student & faculty
    cursor.execute("""
    INSERT INTO wallet_transactions (user_id, amount, transaction_type, reference, balance_after, created_at)
    VALUES (1, 500.00, 'credit', 'Initial Welcome Credit', 500.00, ?)
    """, (now_str,))
    cursor.execute("""
    INSERT INTO wallet_transactions (user_id, amount, transaction_type, reference, balance_after, created_at)
    VALUES (1, 50.00, 'debit', 'Breakfast Snack', 450.00, ?)
    """, (now_str,))
    cursor.execute("""
    INSERT INTO wallet_transactions (user_id, amount, transaction_type, reference, balance_after, created_at)
    VALUES (2, 1200.00, 'credit', 'Faculty Meal Allowance Top-up', 1200.00, ?)
    """, (now_str,))

    # Seed Menu Items (with photorealistic images generated and standard fallbacks)
    menu_items = [
        (
            "Artisan Veggie Burger Combo",
            "Snacks",
            "Char-grilled herb patty, melted cheddar, crisp lettuce, farm tomato on a brioche bun with golden fries & dip.",
            120.00, 1, 40, "veg", "/static/images/burger.jpg", 12, 540, 4.9, now_str
        ),
        (
            "Royal Mysore Masala Dosa",
            "Breakfast",
            "Crispy golden crepe smeared with spicy red chutney, stuffed with spiced potato mash, served with coconut chutney & sambar.",
            85.00, 1, 60, "veg", "/static/images/dosa.jpg", 8, 380, 4.9, now_str
        ),
        (
            "Signature Caramel Iced Macchiato",
            "Beverages",
            "Velvety cold-brew espresso with chilled whole milk, rich vanilla syrup, and decadent golden caramel swirl.",
            95.00, 1, 75, "veg", "/static/images/coffee.jpg", 4, 210, 4.8, now_str
        ),
        (
            "Mediterranean Nourish Bowl",
            "Healthy",
            "Fluffy quinoa, creamy avocado, crisp chickpeas, heirloom tomatoes, English cucumber ribbons, and tahini drizzle.",
            140.00, 1, 35, "vegan", "/static/images/salad.jpg", 10, 390, 4.7, now_str
        ),
        (
            "Steaming Idli Sambar Platter (3 pcs)",
            "Breakfast",
            "Melt-in-mouth fermented steamed rice-lentil cakes immersed in hot aromatic drumstick sambar and fresh mint chutney.",
            55.00, 1, 50, "veg", "/static/images/dosa.jpg", 5, 260, 4.6, now_str
        ),
        (
            "Paneer Butter Masala Thali",
            "Lunch",
            "Tender cottage cheese cubes simmered in rich buttery tomato cashew gravy, served with 2 butter naans, jeera rice, and salad.",
            160.00, 1, 45, "veg", "/static/images/burger.jpg", 15, 680, 4.9, now_str
        ),
        (
            "Schezwan Wok Hakka Noodles",
            "Lunch",
            "Wok-tossed noodles with shredded bell peppers, cabbage, spring onion, and house spicy garlic Schezwan sauce.",
            110.00, 1, 50, "veg", "/static/images/salad.jpg", 10, 480, 4.6, now_str
        ),
        (
            "Classic Bombay Vada Pav (2 pcs)",
            "Snacks",
            "Spiced potato fritters encased in fluffy pav buns, layered with fiery garlic chutney and fried green chillies.",
            45.00, 1, 80, "veg", "/static/images/burger.jpg", 5, 320, 4.8, now_str
        ),
        (
            "Spiced Kulhad Adrak Chai",
            "Beverages",
            "Slow-brewed Assam tea leaves infused with crushed fresh ginger, green cardamom, and served steaming in an earthen kulhad.",
            25.00, 1, 120, "veg", "/static/images/coffee.jpg", 3, 90, 4.9, now_str
        ),
        (
            "Fresh Alphonso Mango Smoothie",
            "Beverages",
            "Thick blend of real Alphonso mango pulp, chilled Greek yogurt, honey, and crushed pistachio garnish.",
            75.00, 1, 40, "veg", "/static/images/coffee.jpg", 5, 230, 4.8, now_str
        ),
        (
            "Peri-Peri Golden Crinkle Fries",
            "Snacks",
            "Crispy golden crinkle-cut potato fries dusted with tangy, spicy African peri-peri seasoning and garlic mayo dip.",
            65.00, 1, 60, "vegan", "/static/images/burger.jpg", 6, 310, 4.7, now_str
        ),
        (
            "Protein Sprouted Chickpea Salad",
            "Healthy",
            "Sprouted organic chickpeas, pomegranate pearls, diced cucumber, tomatoes, tossed with extra virgin olive oil & chaat masala.",
            90.00, 1, 30, "vegan", "/static/images/salad.jpg", 6, 220, 4.8, now_str
        )
    ]

    cursor.executemany("""
    INSERT INTO menu_items (name, category, description, price, is_available, stock_quantity, dietary_type, image_url, prep_time_minutes, calories, rating, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, menu_items)

    # Seed Sample Orders so the Kitchen Display and Admin Analytics have active data
    t_minus_30 = (datetime.now() - timedelta(minutes=30)).isoformat()
    t_minus_18 = (datetime.now() - timedelta(minutes=18)).isoformat()
    t_minus_8 = (datetime.now() - timedelta(minutes=8)).isoformat()
    t_minus_3 = (datetime.now() - timedelta(minutes=3)).isoformat()

    orders = [
        ("ORD-1001", "TK-101", 1, 205.00, 0.0, 205.00, "wallet", "paid", "ready", "Extra chutney please", t_minus_30, t_minus_8),
        ("ORD-1002", "TK-102", 2, 255.00, 0.0, 255.00, "wallet", "paid", "preparing", "Less spicy noodles", t_minus_18, t_minus_8),
        ("ORD-1003", "TK-103", 1, 140.00, 0.0, 140.00, "wallet", "paid", "pending", "No dressing on salad", t_minus_3, t_minus_3),
        ("ORD-1004", "TK-104", 2, 120.00, 0.0, 120.00, "wallet", "paid", "completed", "Takeaway packaging", t_minus_30, t_minus_18),
    ]

    cursor.executemany("""
    INSERT INTO orders (order_number, token_number, user_id, total_amount, discount_amount, final_amount, payment_method, payment_status, order_status, special_instructions, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, orders)

    # Order Items
    order_items = [
        # ORD-1001
        (1, 1, "Artisan Veggie Burger Combo", 1, 120.00, 120.00),
        (1, 2, "Royal Mysore Masala Dosa", 1, 85.00, 85.00),
        # ORD-1002
        (2, 6, "Paneer Butter Masala Thali", 1, 160.00, 160.00),
        (2, 3, "Signature Caramel Iced Macchiato", 1, 95.00, 95.00),
        # ORD-1003
        (3, 4, "Mediterranean Nourish Bowl", 1, 140.00, 140.00),
        # ORD-1004
        (4, 1, "Artisan Veggie Burger Combo", 1, 120.00, 120.00),
    ]

    cursor.executemany("""
    INSERT INTO order_items (order_id, item_id, item_name, quantity, unit_price, subtotal)
    VALUES (?, ?, ?, ?, ?, ?)
    """, order_items)

    conn.commit()
