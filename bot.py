import os
import asyncio
import replicate
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ======================
# TOKENS (خیلی مهم)
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# بررسی توکن‌ها
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is missing!")

if not REPLICATE_API_TOKEN:
    raise Exception("REPLICATE_API_TOKEN is missing!")

client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام!\n✏ یک متن بفرست تا برات عکس بسازم"
    )

# ======================
# AI IMAGE (FLUX FIXED)
# ======================
def generate_image(prompt):
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
# TEXT HANDLER
# ======================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text

    msg = await update.message.reply_text("⏳ در حال ساخت تصویر...")

    loop = asyncio.get_event_loop()
    image, error = await loop.run_in_executor(None, generate_image, prompt)

    # ❌ اگر خطا بود
    if error:
        await msg.edit_text(f"❌ خطا:\n{error}")
        return

    # ❌ اگر چیزی برنگشت
    if not image:
        await msg.edit_text("❌ هیچ خروجی دریافت نشد (API مشکل دارد)")
        return

    # ارسال عکس
    await msg.delete()

    await update.message.reply_photo(
        photo=image,
        caption="✅ تصویر ساخته شد"
    )

# ======================
# MAIN
# ======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
