import aiosqlite
from aiosqlite import Connection

from bot.config import get_config

config = get_config()
DB_PATH = config.db_path

async def create_table_routes(db: Connection):
    await db.execute("""
                CREATE TABLE IF NOT EXISTS routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    departure TEXT,
                    destination TEXT,
                    cost REAL
                )
            """)


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


