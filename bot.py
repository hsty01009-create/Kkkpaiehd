import os
import json
import time
import requests
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

# ======================
# TOKENS
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
MUSIC_MODEL = "facebook/musicgen-small"

DB_FILE = "database.json"

# ======================
# DB
# ======================
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

db = load_db()

# ======================
# UI
# ======================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 ساخت عکس", callback_data="img")],
        [InlineKeyboardButton("🎵 ساخت موزیک", callback_data="music")],
        [InlineKeyboardButton("⚙️ زبان", callback_data="lang")]
    ])

def languages():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="fa")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="en")]
    ])

# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    db[user_id] = db.get(user_id, {
        "lang": "fa",
        "accepted": False
    })
    save_db(db)

    text = "📜 قوانین را قبول دارید؟\n\nسازنده: امیر علی فروزان اصل"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ قبول دارم", callback_data="accept")]
    ])

    await update.message.reply_text(text, reply_markup=keyboard)

# ======================
# CALLBACK
# ======================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    if query.data == "accept":
        db[user_id]["accepted"] = True
        save_db(db)
        await query.edit_message_text("✔ قوانین تایید شد")
        await query.message.reply_text("منو:", reply_markup=main_menu())

    elif query.data == "img":
        await query.message.reply_text("✏ متن عکس را بفرست")

    elif query.data == "music":
        await query.message.reply_text("🎵 متن موزیک را بفرست (تا 5 دقیقه)")

    elif query.data == "lang":
        await query.message.reply_text("زبان را انتخاب کن:", reply_markup=languages())

    elif query.data in ["fa", "en"]:
        db[user_id]["lang"] = query.data
        save_db(db)
        await query.message.reply_text("✔ زبان تنظیم شد")

# ======================
# IMAGE AI (FIXED)
# ======================
def generate_image(prompt):
    url = f"https://api-inference.huggingface.co/models/{IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    r = requests.post(
        url,
        headers=headers,
        json={"inputs": prompt},
        timeout=300
    )

    if "application/json" in r.headers.get("content-type", ""):
        return None, r.text

    if r.status_code != 200:
        return None, f"ERROR {r.status_code}"

    file = "image.jpg"
    with open(file, "wb") as f:
        f.write(r.content)

    return file, None

# ======================
# MUSIC AI (FIXED)
# ======================
def generate_music(prompt):
    url = f"https://api-inference.huggingface.co/models/{MUSIC_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    r = requests.post(
        url,
        headers=headers,
        json={"inputs": prompt},
        timeout=300
    )

    if "application/json" in r.headers.get("content-type", ""):
        return None, r.text

    if r.status_code != 200:
        return None, f"ERROR {r.status_code}"

    file = "music.mp3"
    with open(file, "wb") as f:
        f.write(r.content)

    return file, None

# ======================
# MESSAGE HANDLER
# ======================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in db or not db[user_id].get("accepted"):
        await update.message.reply_text("❌ اول قوانین را قبول کن")
        return

    # IMAGE
    if context.user_data.get("mode") == "img":
        await update.message.reply_text("⏳ در حال ساخت عکس... 0%")

        file, err = generate_image(text)

        if err:
            await update.message.reply_text(f"❌ خطا:\n{err}")
            return

        await update.message.reply_photo(
            photo=open(file, "rb"),
            caption="✔ ساخته شد"
        )

        return

    # MUSIC
    if context.user_data.get("mode") == "music":
        await update.message.reply_text("⏳ در حال ساخت موزیک... تا 5 دقیقه")

        file, err = generate_music(text)

        if err:
            await update.message.reply_text(f"❌ خطا:\n{err}")
            return

        await update.message.reply_audio(
            audio=open(file, "rb"),
            caption="✔ موزیک ساخته شد"
        )

        return

# ======================
# MAIN MENU CONTROL
# ======================
async def menu_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🖼 ساخت عکس":
        context.user_data["mode"] = "img"
        await update.message.reply_text("✏ متن عکس را بفرست")

    elif text == "🎵 ساخت موزیک":
        context.user_data["mode"] = "music"
        await update.message.reply_text("✏ متن موزیک را بفرست")

# ======================
# MAIN
# ======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_control))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
