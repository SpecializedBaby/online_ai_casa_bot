import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_months_keyboard() -> InlineKeyboardMarkup:
    today = datetime.date.today()
    months = [(today + datetime.timedelta(days=30 * i)).strftime("%B") for i in range(5)]
    keyboard = [
        [InlineKeyboardButton(text=month, callback_data=f"{month}")]
        for month in months
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_list_offers(offers: list) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=f"{offer.name} - {offer.price}€", callback_data=f"offer_{offer.id}")]
        for offer in offers
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
