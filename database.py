import sqlite3

DATABASE = "luxury_wheels.db"

def connect():

    """ Creates connection to database """

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def create_tables():

    """ Creates database table """

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
            )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            license_plate TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            transmission TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            image_path TEXT,
            daily_price REAL NOT NULL,
            last_revision_date TEXT,
            next_revision_date TEXT,
            last_inspection_date TEXT,
            next_inspection_date TEXT,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            nif TEXT NOT NULL UNIQUE,
            email TEXT,
            phone TEXT,
            address TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            vehicle_id INTEGER NOT NULL,
            payment_method_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            daily_price REAL NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
            FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
        )
    """)

    conn.commit()
    conn.close()

    print("Tables created successfully!")


def show_tables():
    """Displays all tables in the database."""

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """)

    tables = cursor.fetchall()

    for table in tables:
        print(table["name"])

    conn.close()



if __name__ == "__main__":
    create_tables()