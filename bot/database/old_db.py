import aiosqlite
from typing import List, Dict

from aiosqlite import Connection

from bot.config import get_config
from bot.database.notifications import create_table_notification
from bot.database.order import create_table_orders
from bot.database.payment import create_table_payment
from bot.database.routes import create_table_routes
from bot.database.users import create_user_table

config = get_config()

DB_PATH = config.db_path


async def init_db(db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await create_user_table(db=db)
        await create_table_routes(db=db)
        await create_table_notification(db=db)
        await create_table_payment(db=db)
        await create_table_orders(db=db)

        await db.commit()

async def create_table_routes(db: Connection):
    await db.execute("""
                CREATE TABLE IF NOT EXISTS routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    departure TEXT,
                    destination TEXT,
                    cost REAL
                )
            """)

async def create_table_payment(db: Connection):
    await db.execute("""
                CREATE TABLE IF NOT EXISTS payment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_method TEXT,
                    invoice_id INTEGER
                )
            """)

async def create_table_orders(db: Connection):
    await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    router_id INTEGER,
                    notification_id INTEGER NOT NULL,
                    payment_id INTEGER NOT NULL,
                    travel_date TEXT NOT NULL,
                    seat_type TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    price REAL,
                    status TEXT DEFAULT 'unpaid',
                    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(router_id) REFERENCES routes(id),
                    FOREIGN KEY(notification_id) REFERENCES notifications(id),
                    FOREIGN KEY(payment_id) REFERENCES payment(id)
                )
            """)


async def create_user_table(db: Connection):
    await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   telegram_id INTEGER UNIQUE NOT NULL,
                   username TEXT,
                   full_name TEXT,
                   birthday TEXT,
                   address TEXT,
                   email TEXT
                )
            """)

async def save_user(data: dict, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            INSERT INTO users (telegram_id, username, full_name, birthday, address, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
            data["telegram_id"], data["username"], data["full_name"], data["birthday"], data["address"], data["email"]
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

async def mark_ticket_sent(order_id: int, db_path=DB_PATH) -> None:
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

async def create_table_notification(db: Connection):
    await db.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notified_admin BOOLEAN DEFAULT 0,
                    ticket_sent_user BOOLEAN DEFAULT 0
                )
            """)


async def mark_notified_admin(order_id: int, db_path=DB_PATH) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE orders SET notified = 1 WHERE id = ?", (order_id,))
        await db.commit()

async def save_order(data: dict, db_path=DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            INSERT INTO orders (user_id, router_id, notification_id, travel_date, seat_type, quantity, price, invoice_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["user_id"], data["username"], data["departure"],
            data["destination"], data["travel_date"],
            data["seat_type"], data["quantity"], data["price"],
            data["invoice_id"],
        ))
        await db.commit()

async def save_route(dep: str, dest: str, cost: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO routes (departure, destination, cost) VALUES (?, ?, ?)",
            (dep.title(), dest.title(), cost)
        )
        await db.commit()


async def get_route_price(departure: str, destination: str) -> float | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT cost FROM routes WHERE departure = ? AND destination = ?",
            (departure.title(), destination.title())
        )
        result = await cursor.fetchone()
        return result[0] if result else None