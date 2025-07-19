from typing import List, Dict


orders: List[Dict] = []


def save_order(order: Dict):
    orders.append(order)


def get_all_orders() -> List[Dict]:
    return orders
