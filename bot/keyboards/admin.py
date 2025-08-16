from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def admin_general_keyboard_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="/mark_paid"), KeyboardButton(text="/export_paid")],
        [KeyboardButton(text="/cancel_order"), KeyboardButton(text="/attach_invoice")],
        [KeyboardButton(text="/add_route"), KeyboardButton(text="/orders")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, is_persistent=True)
