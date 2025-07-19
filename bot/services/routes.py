#  Later have to replace this with a database

ROUTES = {
    ("Berlin", "Munich"): 20.0,
    ("Berlin", "Hamburg"): 15.0,
    ("Munich", "Frankfurt"): 18.0,
    ("Hamburg", "Cologne"): 22.0,
}

DEFAULT_PRICE = 10.0


def get_route_price(departure: str, destination: str) -> float:
    route = (departure.title(), destination.title())
    return ROUTES.get(route, DEFAULT_PRICE)
