import aiosqlite
from aiosqlite import Connection

from bot.config import get_config

config = get_config()
DB_PATH = config.db_path


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
