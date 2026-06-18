import os
import json
import asyncio
import replicate
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ================= TOKENS =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

client = replicate.Client(api_token=REPLICATE_API_TOKEN)

DB_FILE = "db.json"

# ================= DB =================
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🖼 ساخت عکس", callback_data="img")]
    ]

    await update.message.reply_text(
        "👋 سلام!\nمتن عکس را بفرست",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= IMAGE =================
def make_image(prompt):
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

# ================= TEXT =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    msg = await update.message.reply_text("⏳ در حال ساخت...")

    loop = asyncio.get_event_loop()
    result, err = await loop.run_in_executor(None, make_image, user_text)

    if err:
        await msg.edit_text(f"❌ خطا:\n{err}")
        return

    keyboard = [
        [InlineKeyboardButton("⬇️ دانلود", url=result)]
    ]

    await msg.delete()

    await update.message.reply_photo(
        photo=result,
        caption="✅ ساخته شد",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
