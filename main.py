import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

from database import *
from texts import TEXTS
from image_ai import generate_image_url
from sticker import create_sticker
from image_edit import edit_image

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

user_state = {}

WAIT_IMG = "img"
WAIT_STICKER = "stk"
WAIT_EDIT = "edit"


# 🎛 MENU (Dynamic Language)
def menu(lang):
    t = TEXTS.get(lang, TEXTS["fa"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 AI Image", callback_data="img")],
        [InlineKeyboardButton("🎭 Sticker", callback_data="stk")],
        [InlineKeyboardButton("🎨 Edit Image", callback_data="edit")],
        [InlineKeyboardButton("🌍 Language", callback_data="lang")]
    ])


# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    invited = context.args[0] if context.args else None

    add_user(user.id, invited)

    # 💰 rewards
    add_coins(user.id, 100)

    if invited:
        add_coins(int(invited), 300)

    cur = get_user(user.id)
    lang = cur[2] if cur else "fa"

    await update.message.reply_text(
        TEXTS[lang]["rules"],
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Accept", callback_data="accept")]
        ])
    )


# 🔘 BUTTONS
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    user = get_user(uid)
    lang = user[2] if user else "fa"

    if q.data == "accept":
        await q.message.edit_text(TEXTS[lang]["welcome"], reply_markup=menu(lang))

    elif q.data == "img":
        user_state[uid] = WAIT_IMG
        await q.message.reply_text(TEXTS[lang]["send_prompt"])

    elif q.data == "stk":
        user_state[uid] = WAIT_STICKER
        await q.message.reply_text(TEXTS[lang]["send_photo"])

    elif q.data == "edit":
        user_state[uid] = WAIT_EDIT
        await q.message.reply_text("📸 Send photo to edit")


# 🧠 TEXT (AI IMAGE)
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if user_state.get(uid) == WAIT_IMG:
        url = generate_image_url(update.message.text)
        await update.message.reply_photo(photo=url)
        user_state.pop(uid, None)


# 🖼 PHOTO HANDLER
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    file = await update.message.photo[-1].get_file()

    path = f"{uid}.jpg"
    await file.download_to_drive(path)

    if user_state.get(uid) == WAIT_STICKER:
        st = create_sticker(path)
        await update.message.reply_sticker(sticker=open(st, "rb"))
        user_state.pop(uid, None)

    elif user_state.get(uid) == WAIT_EDIT:
        out = edit_image(path)
        await update.message.reply_photo(photo=open(out, "rb"))
        user_state.pop(uid, None)


# 🚀 RUN
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("PRO Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
