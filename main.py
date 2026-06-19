import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# ================= DB =================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    lang TEXT DEFAULT 'fa',
    coins INTEGER DEFAULT 100
)
""")
conn.commit()

# ================= LANG =================
LANGS = {
    "fa": "فارسی",
    "en": "English",
    "ar": "العربية",
    "tr": "Türkçe",
    "fr": "Français",
    "es": "Español",
    "ru": "Русский"
}

RULES = """
📜 Rules

1. Respect required
2. No spam
3. No abuse
4. No insult
5. User is responsible
6. Data is stored
7. Admin not responsible
8. Rules may change
9. Continue = accept rules
"""

# ================= HELPERS =================
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def create_user(user_id):
    if not get_user(user_id):
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

def set_lang(user_id, lang):
    cursor.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
    conn.commit()

def get_lang(user_id):
    user = get_user(user_id)
    return user[1]

def get_coins(user_id):
    user = get_user(user_id)
    return user[2]

# ================= UI =================
def main_menu(lang):
    if lang == "fa":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🌍 زبان", callback_data="lang")],
            [InlineKeyboardButton("💰 سکه", callback_data="coins")],
            [InlineKeyboardButton("📜 قوانین", callback_data="rules")]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🌍 Language", callback_data="lang")],
            [InlineKeyboardButton("💰 Coins", callback_data="coins")],
            [InlineKeyboardButton("📜 Rules", callback_data="rules")]
        ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)

    lang = get_lang(user_id)

    text = "✨ خوش آمدی" if lang == "fa" else "✨ Welcome"

    await update.message.reply_text(text, reply_markup=main_menu(lang))

# ================= CALLBACK =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    create_user(user_id)

    data = query.data

    # حذف دکمه‌ها
    await query.edit_message_reply_markup(reply_markup=None)

    # ========= LANGUAGE =========
    if data == "lang":
        keyboard = [
            [InlineKeyboardButton(v, callback_data=f"set_{k}")]
            for k, v in LANGS.items()
        ]
        await query.message.reply_text("Select Language:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ========= SET LANG =========
    elif data.startswith("set_"):
        lang = data.split("_")[1]
        set_lang(user_id, lang)
        await query.message.reply_text(f"✅ Language set: {LANGS[lang]}")

    # ========= COINS =========
    elif data == "coins":
        coins = get_coins(user_id)
        await query.message.reply_text(f"💰 Coins: {coins}")

    # ========= RULES =========
    elif data == "rules":
        await query.message.reply_text(RULES)

# ================= TEXT (AI IMAGE READY) =================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # لینک Pollinations AI
    url = f"https://image.pollinations.ai/prompt/{text}"

    await update.message.reply_photo(photo=url)

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
