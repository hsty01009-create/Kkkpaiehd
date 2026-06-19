from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def rules_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ قبول", callback_data="accept"),
            InlineKeyboardButton(text="❌ رد", callback_data="reject")
        ]
    ])


def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang_fa"),
            InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")
        ],
        [
            InlineKeyboardButton(text="🇮🇳 हिन्दी", callback_data="lang_hi"),
            InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr"),
            InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang_fr")
        ]
    ])


def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🖼 عکس", callback_data="image"),
            InlineKeyboardButton(text="🧊 استیکر", callback_data="sticker")
        ],
        [
            InlineKeyboardButton(text="💰 سکه", callback_data="coins"),
            InlineKeyboardButton(text="🎁 روزانه", callback_data="daily")
        ],
        [
            InlineKeyboardButton(text="🌍 زبان", callback_data="lang")
        ]
    ])
