from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def rules():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ قبول قوانین", callback_data="accept")]
    ])

def lang():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="fa"),
         InlineKeyboardButton(text="🇺🇸 English", callback_data="en")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ru"),
         InlineKeyboardButton(text="🇪🇸 Español", callback_data="es")],
        [InlineKeyboardButton(text="🇮🇳 हिन्दी", callback_data="hi"),
         InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="tr"),
         InlineKeyboardButton(text="🇫🇷 Français", callback_data="fr")]
    ])

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 ادیت عکس", callback_data="edit")],
        [InlineKeyboardButton(text="🧊 استیکر", callback_data="sticker")],
        [InlineKeyboardButton(text="💰 سکه", callback_data="coins")],
        [InlineKeyboardButton(text="👥 دعوت", callback_data="invite")]
    ])
