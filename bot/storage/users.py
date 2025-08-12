import aiosqlite
from aiosqlite import Connection

from bot.config import get_config

config = get_config()
DB_PATH = config.db_path


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

