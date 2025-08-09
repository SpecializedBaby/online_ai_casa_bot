import datetime

from aiocryptopay.models.invoice import Invoice
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def general_keyboard_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="/db_pass")],
        [KeyboardButton(text="/start"), KeyboardButton(text="/book")],
        [KeyboardButton(text="/my_orders"), KeyboardButton(text="/help")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, is_persistent=True)


# Keyboard Monthly DB Pass
def get_months_keyboard() -> InlineKeyboardMarkup:
    today = datetime.date.today()
    months = [(today + datetime.timedelta(days=30 * i)).strftime("%B") for i in range(5)]
    keyboard = [
        [InlineKeyboardButton(text=month, callback_data=f"de_ticket:{month}")]
        for month in months
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_keyboard_seat_classes() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="Standard", callback_data="standard"),
            InlineKeyboardButton(text="Business", callback_data="business"),
            InlineKeyboardButton(text="Sleeper", callback_data="sleeper"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_keyboard_pay_btn(invoice: Invoice) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="💸 Pay with CryptoBot", url=invoice.bot_invoice_url)]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return inline_keyboard


def get_keyboard_quantity_number() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="1", callback_data="1"),
            InlineKeyboardButton(text="2", callback_data="2"),
            InlineKeyboardButton(text="3", callback_data="3"),
            InlineKeyboardButton(text="4", callback_data="4"),
            InlineKeyboardButton(text="5", callback_data="5"),
            InlineKeyboardButton(text="6", callback_data="6"),
            InlineKeyboardButton(text="7", callback_data="7"),
            InlineKeyboardButton(text="8", callback_data="8"),
            InlineKeyboardButton(text="9", callback_data="9"),
            InlineKeyboardButton(text="10", callback_data="10"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_keyboard_confirmation() -> InlineKeyboardMarkup:
    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_order")]
    ])
    return confirm_kb


def get_keyboard_payment_method() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="💸 CryptoBot", callback_data="pay_cryptobot")],
        [InlineKeyboardButton(text="💵 Manual", callback_data="pay_manual")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
