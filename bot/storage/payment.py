from aiosqlite import Connection

from bot.config import get_config

config = get_config()
DB_PATH = config.db_path


async def create_table_payment(db: Connection):
    await db.execute("""
                CREATE TABLE IF NOT EXISTS payment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_method TEXT,
                    invoice_id INTEGER
                )
            """)
