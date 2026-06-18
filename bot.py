import os
import asyncio
import replicate

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
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

client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# =========================
# USER STATE
# =========================
user_data = {}

# =========================
# START MENU (PRO BUTTONS)
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎨 ساخت تصویر", callback_data="img")],
        [InlineKeyboardButton("⚙️ انتخاب مدل", callback_data="model")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ]

    await update.message.reply_text(
        "🚀 ربات PRO آماده است\nیکی از گزینه‌ها را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# BUTTON HANDLER
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if query.data == "img":
        user_data[uid] = {"mode": "prompt"}

        await query.message.reply_text(
            "✍ ساخته شد توسط امیرعلی فروزان‌اصل:متن تصویر را بفرست"
        )

    elif query.data == "model":
        keyboard = [
            [InlineKeyboardButton("🔥 FLUX", callback_data="m_flux")],
            [InlineKeyboardButton("🎯 IMAGEN-4", callback_data="m_imagen")]
        ]

        await query.message.reply_text(
            "⚙️ مدل را انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "m_flux":
        user_data[uid] = user_data.get(uid, {})
        user_data[uid]["model"] = "flux"

        await query.message.reply_text("✅ مدل FLUX فعال شد")

    elif query.data == "m_imagen":
        user_data[uid] = user_data.get(uid, {})
        user_data[uid]["model"] = "imagen"

        await query.message.reply_text("✅ مدل Imagen-4 فعال شد")

    elif query.data == "help":
        await query.message.reply_text(
            "🧠 راهنما:\n"
            "- متن بفرست → تصویر ساخته می‌شود\n"
            "- مدل را انتخاب کن\n"
            "- ساخت تصویر AI"
        )

# =========================
# GENERATE IMAGE (PRO)
# =========================
def generate(prompt, model):
    try:
        if model == "imagen":
            output = client.run(
                "google/imagen-4",
                input={
                    "prompt": prompt,
                    "aspect_ratio": "1:1",
                    "safety_filter_level": "block_medium_and_above"
                }
            )
        else:
            output = client.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": prompt,
                    "aspect_ratio": "1:1"
                }
            )

        return output, None

    except Exception as e:
        return None, str(e)

# =========================
# MESSAGE HANDLER
# =========================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    model = user_data.get(uid, {}).get("model", "flux")

    msg = await update.message.reply_text("⏳ در حال ساخت تصویر...")

    loop = asyncio.get_event_loop()
    image, error = await loop.run_in_executor(None, generate, text, model)

    if error:
        await msg.edit_text(f"❌ خطا:\n{error}")
        return

    await msg.delete()

    await update.message.reply_photo(
        photo=image,
        caption=f"✅ ساخته شد | مدل: {model.upper()}"
    )

# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🚀 PRO BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
