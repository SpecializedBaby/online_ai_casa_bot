import aiosqlite
from typing import List, Dict

DB_PATH = "orders.db"


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
                price REAL,
                invoice_id INTEGER,
                status TEXT DEFAULT 'unpaid'
            )
        """)
        await db.commit()

async def save_order(data: Dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO orders (user_id, username, departure, destination, travel_date, seat_type, price, invoice_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["user_id"], data["username"], data["departure"],
            data["destination"], data["travel_date"],
            data["seat_type"], data["price"], data["invoice_id"]
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
        rows = await cursor.fetchall()
        return rows
