import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database import *
from texts import LANGS, welcome
from rules import RULES
from image_tools import generate_image_url
from sticker import create_sticker

BOT_TOKEN = os.getenv("BOT_TOKEN")

user_state = {}

IMG = "img"
STK = "stk"


# ================= MENU =================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 Image", callback_data="img")],
        [InlineKeyboardButton("🎭 Sticker", callback_data="stk")],
        [InlineKeyboardButton("💰 Coins", callback_data="coins")],
        [InlineKeyboardButton("🌍 Language", callback_data="lang")]
    ])


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    invited_by = None
    if context.args:
        try:
            invited_by = int(context.args[0])
        except:
            pass

    add_user(user.id, invited_by)

    await update.message.reply_text(
        RULES,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ قبول قوانین", callback_data="ok")]
        ])
    )


# ================= CALLBACK =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    data = q.data

    await q.edit_message_reply_markup(reply_markup=None)

    if data == "ok":
        await q.message.reply_text("👋 منو:", reply_markup=menu())

    elif data == "img":
        user_state[uid] = IMG
        await q.message.reply_text("✍ متن عکس را بفرست")

    elif data == "stk":
        user_state[uid] = STK
        await q.message.reply_text("📷 عکس بفرست")

    elif data == "coins":
        coins = get_coins(uid)
        await q.message.reply_text(f"💰 {coins}")

    elif data == "lang":
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"l_{code}")]
            for code, name in LANGS.items()
        ]
        await q.message.reply_text(
            "🌍 انتخاب زبان",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("l_"):
        lang = data[2:]
        set_lang(uid, lang)
        coins = get_coins(uid)
        await q.message.reply_text(welcome(lang, coins), reply_markup=menu())


# ================= TEXT =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if user_state.get(uid) == IMG:
        url = generate_image_url(update.message.text)
        await update.message.reply_photo(url)
        user_state.pop(uid, None)


# ================= PHOTO =================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    file = await update.message.photo[-1].get_file()
    path = "temp.jpg"
    await file.download_to_drive(path)

    if user_state.get(uid) == STK:
        out = create_sticker(path)
        await update.message.reply_sticker(out)
        user_state.pop(uid, None)


# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
