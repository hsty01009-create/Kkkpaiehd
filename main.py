import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

from database import *
from texts import *
from rules import RULES
from image_tools import generate_image_url
from sticker import create_sticker

BOT_TOKEN = os.getenv("BOT_TOKEN")

user_state = {}

WAIT_IMG = "img"
WAIT_STICKER = "stk"

def menu(lang):
    if lang == "fa":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🖼 عکس", callback_data="img")],
            [InlineKeyboardButton("🎭 استیکر", callback_data="stk")],
            [InlineKeyboardButton("🌍 زبان", callback_data="lang")]
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Image", callback_data="img")],
        [InlineKeyboardButton("Sticker", callback_data="stk")],
        [InlineKeyboardButton("Language", callback_data="lang")]
    ])

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)

    await update.message.reply_text(
        RULES,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ قبول", callback_data="accept")]
        ])
    )

# CALLBACK
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    if q.data == "accept":
        lang = get_lang(uid)
        await q.message.reply_text("✔️ وارد شدی", reply_markup=menu(lang))

    elif q.data == "img":
        user_state[uid] = WAIT_IMG
        await q.message.reply_text("✍️ متن عکس را بفرست")

    elif q.data == "stk":
        user_state[uid] = WAIT_STICKER
        await q.message.reply_text("📷 عکس بفرست")

    elif q.data == "lang":
        keyboard = []
        row = []
        for k,v in LANGS.items():
            row.append(InlineKeyboardButton(v, callback_data=f"l_{k}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        await q.message.reply_text("🌍 زبان", reply_markup=InlineKeyboardMarkup(keyboard))

    elif q.data.startswith("l_"):
        lang = q.data.split("_")[1]
        set_lang(uid, lang)
        coins = get_coins(uid)
        await q.message.reply_text(welcome(lang, coins), reply_markup=menu(lang))

# TEXT
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if user_state.get(uid) == WAIT_IMG:
        url = generate_image_url(update.message.text)
        await update.message.reply_photo(photo=url)
        user_state.pop(uid)

# PHOTO
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    file = await update.message.photo[-1].get_file()

    if user_state.get(uid) == WAIT_STICKER:
        await file.download_to_drive("in.jpg")
        st = create_sticker("in.jpg")
        await update.message.reply_sticker(sticker=open(st,"rb"))
        user_state.pop(uid)

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
