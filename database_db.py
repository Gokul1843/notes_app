import sqlite3

# Get database connection
def get_db():
    return sqlite3.connect("database.db")

# Initialize database and tables
def init_db():
    db = get_db()
    c = db.cursor()

    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Notes table
    c.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        url TEXT
    )
    """)

    db.commit()
    db.close()
    print("Database and tables initialized ✅")

# Optional: initialize when run directly
if _name_ == "_main_":
    init_db()