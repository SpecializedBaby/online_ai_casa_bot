import aiosqlite

from bot.config import get_config

config = get_config()
DB_PATH = config.db_path


async def get_route_price(departure: str, destination: str) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT price FROM routes WHERE departure = ? AND destination = ?",
            (departure.title(), destination.title())
        )
        result = cursor.fetchone()
        return result[0] if result else None

async def save_route_in_db(dep: str, dest: str, cost: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO routes (departure, destination, cost) VALUES (?, ?, ?)",
            (dep.title(), dest.title(), cost)
        )
        await db.commit()
