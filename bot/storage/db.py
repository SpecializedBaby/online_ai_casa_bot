import aiosqlite
from typing import List, Dict


from bot.config import get_config

config = get_config()

DB_PATH = config.db_path


async def init_db(db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        # create orders table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                departure TEXT,
                destination TEXT,
                travel_date TEXT,
                seat_type TEXT,
                quantity INTEGER DEFAULT 1,
                price REAL,
                payment_method TEXT DEFAULT 'cryptobot',
                invoice_id INTEGER,
                status TEXT DEFAULT 'unpaid',
                ticket_sent BOOLEAN DEFAULT 0,
                created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # create routes table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                departure TEXT,
                destination TEXT,
                cost REAL
            )
        """)
        await db.commit()

async def save_order(data: Dict, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            INSERT INTO orders (user_id, username, departure, destination, travel_date, seat_type, quantity, price, invoice_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["user_id"], data["username"], data["departure"],
            data["destination"], data["travel_date"],
            data["seat_type"], data["quantity"], data["price"],
            data["invoice_id"],
        ))
        await db.commit()

async def get_order_by_id(order_id: int, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id, ))
        return await cursor.fetchone()


async def get_all_orders(db_path=DB_PATH) -> List[Dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders ORDER BY id DESC")
        return await cursor.fetchall()

async def get_unpaid_orders(db_path=DB_PATH) -> List[Dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE status = 'unpaid'")
        return await cursor.fetchall()

async def mark_order_paid(order_id: int, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE orders SET status = 'paid' WHERE id = ?", (order_id,))
        await db.commit()

async def get_user_orders(user_id: int, db_path=DB_PATH) -> List[Dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders WHERE user_id = ? AND status = 'paid' ORDER BY id DESC",
            (user_id,))
        return await cursor.fetchall()

async def get_paid_orders(db_path=DB_PATH) -> List[Dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE status = 'paid'")
        return await cursor.fetchall()

async def mark_order_canceled(order_id: int, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE orders SET status = 'canceled' WHERE id = ?", (order_id,))
        await db.commit()

async def mark_ticket_sent(order_id: int, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE orders SET ticket_sent = 1 WHERE id = ?", (order_id,))
        await db.commit()


async def get_user_id_by_order_id(order_id, db_path=DB_PATH) -> int:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id FROM orders WHERE id = ?", (order_id,))
        row = await cursor.fetchone()
        return row["user_id"] if row else None

async def get_last_order_by_user_id(user_id: int, db_path=DB_PATH) -> dict:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM orders
            WHERE user_id = ?
            ORDER BY created_time DESC
            LIMIT 1
            """, (user_id, )
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

async def update_order_data(order_id: int, db_path=DB_PATH, **fields):
    if not fields:
        raise ValueError("No data to update.")

    set_clause = ", ".join(f"{key} = ?" for key in fields.keys())
    values = list(fields.values()) + [order_id]

    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            f"UPDATE orders SET {set_clause} WHERE id = ?",
            values
        )
        await db.commit()
