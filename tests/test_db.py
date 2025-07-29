import pytest

from bot.storage.db import get_unpaid_orders, mark_order_paid, get_order_by_id, get_paid_orders, mark_ticket_sent, \
    get_all_orders, get_user_id_by_order_id


@pytest.mark.asyncio
async def test_get_unpaid_orders(setup_test_db):
    unpaid = await get_unpaid_orders(db_path=setup_test_db)
    assert len(unpaid) > 0
    assert unpaid[0]["user_id"] == 1001
    assert unpaid[0]["invoice_id"] == "test_invoice_123"

@pytest.mark.asyncio
async def test_mark_order_paid(setup_test_db):
    unpaid_orders = await get_unpaid_orders(db_path=setup_test_db)
    single_order = unpaid_orders[-1]
    order_id = single_order["id"]
    assert single_order["status"] == "unpaid"
    await mark_order_paid(order_id=order_id, db_path=setup_test_db)
    refresh_order = await get_order_by_id(order_id=order_id, db_path=setup_test_db)
    assert refresh_order["id"] == order_id
    assert refresh_order["status"] == "paid"
    assert refresh_order in await get_paid_orders(db_path=setup_test_db)


@pytest.mark.asyncio
async def test_mark_ticket_sent(setup_test_db):
    paid_order_list = await get_paid_orders(db_path=setup_test_db)
    order_id = paid_order_list[-1]["id"]
    await mark_ticket_sent(order_id=order_id, db_path=setup_test_db)
    refresh_order = await get_order_by_id(order_id=order_id, db_path=setup_test_db)
    assert refresh_order["id"] == order_id
    assert refresh_order["ticket_sent"] == 1  # 1 True | 0 False

@pytest.mark.asyncio
async def test_get_user_id_by_order_id(setup_test_db):
    orders = await get_all_orders(db_path=setup_test_db)
    user_id = orders[-1]["user_id"]
    order_id = orders[-1]["id"]

    assert user_id == await get_user_id_by_order_id(order_id=order_id, db_path=setup_test_db)

