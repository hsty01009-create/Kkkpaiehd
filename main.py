import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from database import *
from texts import LANGS, welcome

TOKEN = os.getenv("BOT_TOKEN")

# ---------- MENU ----------
def menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌍 Language", callback_data="lang"),
            InlineKeyboardButton("💰 Coins", callback_data="coins")
        ],
        [
            InlineKeyboardButton("📜 Rules", callback_data="rules"),
            InlineKeyboardButton("👥 Invite", callback_data="invite")
        ],
        [
            InlineKeyboardButton("🖼 Image", callback_data="img")
        ]
    ])

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)

    coins = get_coins(user.id)

    await update.message.reply_text(
        welcome("FA", coins),
        reply_markup=menu()
    )

# ---------- CALLBACK ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    data = q.data

    await q.edit_message_reply_markup(reply_markup=None)

    # 🌍 LANG
    if data == "lang":
        keys = []
        row = []
        for k, v in LANGS.items():
            row.append(InlineKeyboardButton(v, callback_data=f"set_{k}"))
            if len(row) == 2:
                keys.append(row)
                row = []
        if row:
            keys.append(row)

        await q.message.reply_text("Choose language:", reply_markup=InlineKeyboardMarkup(keys))

    # 💰 COINS
    elif data == "coins":
        await q.message.reply_text(f"💰 Coins: {get_coins(user_id)}")

    # 📜 RULES
    elif data == "rules":
        await q.message.reply_text("""
📜 Rules:
1. Respect
2. No spam
3. No abuse
4. Use responsibly
5. Data stored
6. Admin not responsible
""")

    # 👥 INVITE
    elif data == "invite":
        link = f"https://t.me/YOUR_BOT?start={user_id}"
        await q.message.reply_text(f"👥 Invite link:\n{link}\n\n+200 coins per invite")

    # 🖼 IMAGE
    elif data == "img":
        await q.message.reply_text("✏️ Send text for image")

    # 🌍 SET LANGUAGE
    elif data.startswith("set_"):
        lang = data.split("_")[1]
        set_lang(user_id, lang)
        await q.message.reply_text(f"✅ Language set to {LANGS[lang]}")

# ---------- IMAGE ----------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    url = f"https://image.pollinations.ai/prompt/{text}"
    await update.message.reply_photo(photo=url)

# ---------- APP ----------
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
