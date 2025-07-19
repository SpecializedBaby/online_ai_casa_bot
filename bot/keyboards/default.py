from aiocryptopay.models.invoice import Invoice
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard_seat_classes() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Standard"), KeyboardButton(text="Business")],
        [KeyboardButton(text="Sleeper")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_keyboard_pay_btn(invoice: Invoice) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="💸 Pay with CryptoBot", url=invoice.bot_invoice_url)]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return inline_keyboard
