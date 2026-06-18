import os
import asyncio
import replicate

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# =========================
# TOKENS
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing")

if not REPLICATE_API_TOKEN:
    raise Exception("REPLICATE_API_TOKEN missing")

client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# =========================
# USER STATE
# =========================
user_mode = {}  # img or edit
user_image = {}

# =========================
# START MENU
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎨 ساخت عکس", callback_data="img")],
        [InlineKeyboardButton("✏️ ادیت عکس", callback_data="edit")]
    ]

    await update.message.reply_text(
        "🚀 ربات حرفه‌ای آماده است\nیکی را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# BUTTONS
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    if q.data == "img":
        user_mode[uid] = "img"
        await q.message.reply_text("✍ متن عکس را بفرست:ساخته شده توسط امیر علی فروزان اصل")

    elif q.data == "edit":
        user_mode[uid] = "edit"
        await q.message.reply_text("📸 اول عکس بفرست بعد متن ادیت")

# =========================
# IMAGE GENERATION
# =========================
def make_image(prompt):
    return client.run(
        "black-forest-labs/flux-schnell",
        input={
            "prompt": prompt,
            "aspect_ratio": "1:1"
        }
    )

# =========================
# IMAGE EDIT
# =========================
def edit_image(image_path, prompt):
    return client.run(
        "black-forest-labs/flux-kontext-pro",
        input={
            "image": open(image_path, "rb"),
            "prompt": prompt
        }
    )

# =========================
# TEXT HANDLER
# =========================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    mode = user_mode.get(uid, "img")

    msg = await update.message.reply_text("⏳ در حال پردازش...")

    loop = asyncio.get_event_loop()

    try:
        if mode == "img":
            result = await loop.run_in_executor(None, make_image, text)

        elif mode == "edit":
            if uid not in user_image:
                await msg.edit_text("❌ اول عکس بفرست")
                return

            result = await loop.run_in_executor(
                None,
                edit_image,
                user_image[uid],
                text
            )

        else:
            result = await loop.run_in_executor(None, make_image, text)

        await msg.delete()

        await update.message.reply_photo(
            photo=result,
            caption="✅ ساخته شد"
        )

    except Exception as e:
        await msg.edit_text(f"❌ خطا:\n{e}")

# =========================
# PHOTO HANDLER (FOR EDIT)
# =========================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    file = await update.message.photo[-1].get_file()
    path = f"{uid}.jpg"
    await file.download_to_drive(path)

    user_image[uid] = path

    await update.message.reply_text("📸 عکس دریافت شد، حالا متن ادیت را بفرست")

# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("🚀 BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
