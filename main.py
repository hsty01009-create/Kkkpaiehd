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
from image_edit import enhance

BOT_TOKEN = os.getenv("BOT_TOKEN")

state = {}

IMG = "img"
STK = "stk"
EDIT = "edit"


# ================= MENU =================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 AI Image", callback_data="img")],
        [InlineKeyboardButton("🎭 Sticker", callback_data="stk")],
        [InlineKeyboardButton("🎨 Edit Photo", callback_data="edit")],
        [InlineKeyboardButton("💰 Coins", callback_data="coins")],
        [InlineKeyboardButton("🌍 Language", callback_data="lang")]
    ])


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)

    await update.message.reply_text(
        RULES,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Accept", callback_data="ok")]
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
        await q.message.reply_text("🚀 Menu", reply_markup=menu())

    elif data == "img":
        state[uid] = IMG
        await q.message.reply_text("✍ Send text")

    elif data == "stk":
        state[uid] = STK
        await q.message.reply_text("📷 Send photo")

    elif data == "edit":
        state[uid] = EDIT
        await q.message.reply_text("🎨 Send photo")

    elif data == "coins":
        coins = get_coins(uid)
        await q.message.reply_text(f"💰 {coins}")

    elif data == "lang":
        kb = [[InlineKeyboardButton(v, callback_data=f"l_{k}")] for k, v in LANGS.items()]
        await q.message.reply_text("🌍 Select language", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("l_"):
        lang = data[2:]
        set_lang(uid, lang)
        coins = get_coins(uid)
        await q.message.reply_text(welcome(lang, coins), reply_markup=menu())


# ================= TEXT =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if state.get(uid) == IMG:
        url = generate_image_url(update.message.text)
        await update.message.reply_photo(url)
        state.pop(uid, None)


# ================= PHOTO =================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    file = await update.message.photo[-1].get_file()
    path = "file.jpg"
    await file.download_to_drive(path)

    if state.get(uid) == STK:
        out = create_sticker(path)
        with open(out, "rb") as f:
            await update.message.reply_sticker(f)
        state.pop(uid, None)

    elif state.get(uid) == EDIT:
        out = enhance(path)
        await update.message.reply_photo(open(out, "rb"))
        state.pop(uid, None)


# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
