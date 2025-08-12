import aiosqlite
from aiosqlite import Connection

from bot.config import get_config

config = get_config()
DB_PATH = config.db_path


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