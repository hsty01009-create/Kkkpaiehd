from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🎛 منوی اصلی ربات
def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🖼 ساخت عکس", callback_data="image"),
            InlineKeyboardButton(text="🧊 استیکر", callback_data="sticker")
        ],
        [
            InlineKeyboardButton(text="✏️ ادیت عکس", callback_data="edit")
        ],
        [
            InlineKeyboardButton(text="💰 سکه", callback_data="coins"),
            InlineKeyboardButton(text="🎁 روزانه", callback_data="daily")
        ],
        [
            InlineKeyboardButton(text="👤 پروفایل", callback_data="profile"),
            InlineKeyboardButton(text="👥 دعوت", callback_data="invite")
        ],
        [
            InlineKeyboardButton(text="🌍 زبان", callback_data="lang")
        ]
    ])


# 📜 دکمه قوانین
def rules_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ قبول قوانین", callback_data="accept"),
            InlineKeyboardButton(text="❌ رد", callback_data="reject")
        ]
    ])


# 🌍 منوی انتخاب زبان (7 زبان)
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
            InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr")
        ],
        [
            InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang_fr")
        ]
    ])


# 👥 دکمه دعوت دوستان
def invite_kb(bot_username, user_id):
    link = f"https://t.me/{bot_username}?start={user_id}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔗 لینک دعوت", url=link)
        ]
    ])
