import aiosqlite
from typing import List, Dict


from bot.config import get_config

config = get_config()

DB_PATH = config.db_path


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
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
                invoice_id INTEGER,
                status TEXT DEFAULT 'unpaid',
                created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def save_order(data: Dict):
    async with aiosqlite.connect(DB_PATH) as db:
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

async def get_unpaid_orders() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE status = 'unpaid'")
        return await cursor.fetchall()

async def mark_order_paid(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = 'paid' WHERE id = ?", (order_id,))
        await db.commit()

async def get_all_orders() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders ORDER BY id DESC")
        return await cursor.fetchall()

async def get_user_orders(user_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders WHERE user_id = ? AND status = 'paid' ORDER BY id DESC",
            (user_id,))
        return await cursor.fetchall()

async def get_paid_orders() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE status = 'paid'")
        return await cursor.fetchall()

async def mark_order_canceled(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = 'canceled' WHERE id = ?", (order_id,))
        await db.commit()
