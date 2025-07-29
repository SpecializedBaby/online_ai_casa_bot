import pytest
import aiosqlite
import asyncio

import pytest_asyncio

from bot.storage.db import init_db, save_order

TEST_DB_PATH = "test_orders.db"


@pytest.fixture(scope="session")
def event_loop():
    # Use a single event loop for all async tests
    return asyncio.get_event_loop()

@pytest_asyncio.fixture(scope="module")
async def setup_test_db():
    await init_db(db_path=TEST_DB_PATH)

    # Clean existing orders
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        await db.execute("DELETE FROM orders")
        await db.commit()

    # Create test order
    await save_order({
        "user_id": 1001,
        "username": "@test_user",
        "departure": "Station A",
        "destination": "Station B",
        "travel_date": "2025-08-01",
        "seat_type": "Standard",
        "quantity": 2,
        "price": 20.5,
        "invoice_id": "test_invoice_123",
        "payment_method": "cryptobot"
    }, db_path=TEST_DB_PATH)

    yield TEST_DB_PATH  # provide path to use in test

    # Clean on the end the tests
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        await db.execute("DELETE FROM orders")
        await db.commit()
