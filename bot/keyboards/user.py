import datetime

from aiocryptopay.models.invoice import Invoice
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def general_keyboard_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="/db_pass")],
        [KeyboardButton(text="/start"), KeyboardButton(text="/booking")],
        [KeyboardButton(text="/my_bookings"), KeyboardButton(text="/help")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, is_persistent=True)


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
        [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 11)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_keyboard_confirmation() -> InlineKeyboardMarkup:
    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_booking")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_booking")]
    ])
    return confirm_kb


def get_keyboard_payment_method() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="💸 CryptoBot", callback_data="pay_cryptobot")],
        [InlineKeyboardButton(text="💵 Manual", callback_data="pay_manual")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
