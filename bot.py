import os
import asyncio
import replicate
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ======================
# TOKENS
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not BOT_TOKEN:
    raise Exception("❌ BOT_TOKEN is missing in Railway Variables!")

if not REPLICATE_API_TOKEN:
    raise Exception("❌ REPLICATE_API_TOKEN is missing in Railway Variables!")

# Replicate client
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# ======================
# START COMMAND
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام!\n✍ ساخته شده توسط:امیر علی فروزان اصل یک متن بفرست تا برات عکس HD بسازم 🚀"
    )

# ======================
# IMAGE GENERATION
# ======================
def generate_image(prompt: str):
    try:
        output = client.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt,
                "aspect_ratio": "1:1",
                "output_format": "webp"
            }
        )
        return output, None

    except Exception as e:
        return None, str(e)

# ======================
# MESSAGE HANDLER
# ======================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    msg = await update.message.reply_text("⏳ در حال ساخت تصویر... لطفاً صبر کن")

    loop = asyncio.get_event_loop()
    image, error = await loop.run_in_executor(None, generate_image, user_text)

    if error:
        await msg.edit_text(f"❌ خطا:\n{error}")
        return

    if not image:
        await msg.edit_text("❌ تصویر ساخته نشد (API مشکل دارد)")
        return

    await msg.delete()

    await update.message.reply_photo(
        photo=image,
        caption="✅ تصویر ساخته شد با AI"
    )

# ======================
# MAIN
# ======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
