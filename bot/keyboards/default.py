from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_keyboard_seat_classes():
    keyboard = [
        [KeyboardButton(text="Standard"), KeyboardButton(text="Business")],
        [KeyboardButton(text="Sleeper")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
