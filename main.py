import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

from database import *
from texts import *
from rules import RULES
from image_tools import generate_image_url
from sticker import create_sticker

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

user_state = {}

WAIT_IMG = "img"
WAIT_STICKER = "stk"

# ================= MENU =================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 Image AI", callback_data="img")],
        [InlineKeyboardButton("🎭 Sticker", callback_data="stk")],
        [InlineKeyboardButton("🌍 Language", callback_data="lang")],
        [InlineKeyboardButton("💰 Coins", callback_data="coins")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    invited = None
    if context.args:
        try:
            invited = int(context.args[0])
        except:
            pass

    add_user(user.id, invited)

    await update.message.reply_text(
        RULES,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Accept", callback_data="accept")]
        ])
    )

# ================= BUTTONS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    data = q.data

    if data == "accept":
        await q.message.reply_text("👋 Welcome!", reply_markup=menu())

    elif data == "img":
        user_state[uid] = WAIT_IMG
        await q.message.reply_text("✍️ Send prompt")

    elif data == "stk":
        user_state[uid] = WAIT_STICKER
        await q.message.reply_text("📷 Send photo")

    elif data == "coins":
        await q.message.reply_text(f"💰 Coins: {get_coins(uid)}")

# ================= TEXT =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if user_state.get(uid) == WAIT_IMG:
        url = generate_image_url(update.message.text)

        await update.message.reply_photo(photo=url, caption="✅ Done")

        user_state.pop(uid, None)

# ================= PHOTO =================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    file = await update.message.photo[-1].get_file()

    if user_state.get(uid) == WAIT_STICKER:
        await file.download_to_drive("in.jpg")

        st = create_sticker("in.jpg")

        with open(st, "rb") as f:
            await update.message.reply_sticker(f)

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
