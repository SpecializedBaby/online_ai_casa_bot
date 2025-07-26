from aiocryptopay.models.invoice import Invoice
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def general_keyboard_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="/book")],
        [KeyboardButton(text="/my_orders"), KeyboardButton(text="/help")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


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


def get_keyboard_quantity_number() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="1"), KeyboardButton(text="2")], [KeyboardButton(text="3")],
        [KeyboardButton(text="4"), KeyboardButton(text="5")], [KeyboardButton(text="6")],
        [KeyboardButton(text="7"), KeyboardButton(text="8")], [KeyboardButton(text="9")],
        [KeyboardButton(text="10"), KeyboardButton(text="11")], [KeyboardButton(text="12")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


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
    return InlineKeyboardMarkup(keyboard=keyboard)
