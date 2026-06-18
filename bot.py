import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= TOKENS =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# ================= MODELS =================
IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
MUSIC_MODEL = "facebook/musicgen-small"

DB_FILE = "database.json"


# ================= DATABASE =================
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}}


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


db = load_db()


# ================= BUTTONS =================
def agree_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ قبول قوانین", callback_data="accept")],
        [InlineKeyboardButton("❌ رد قوانین", callback_data="reject")]
    ])


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 ساخت عکس", callback_data="img")],
        [InlineKeyboardButton("🎵 ساخت موزیک", callback_data="music")]
    ])


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in db["users"]:
        db["users"][user_id] = {
            "accepted": False,
            "warn": 0,
            "blocked": False
        }
        save_db(db)

    await update.message.reply_text(
        "📜 قوانین ربات\n"
        "سازنده: امیر علی فروزان اصل\n\n"
        "آیا قوانین را قبول می‌کنی؟",
        reply_markup=agree_buttons()
    )


# ================= BUTTON HANDLER =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = str(q.from_user.id)

    if q.data == "accept":
        db["users"][user_id]["accepted"] = True
        save_db(db)

        await q.message.edit_text(
            "✅ خوش آمدید",
            reply_markup=main_menu()
        )

    elif q.data == "reject":
        await q.message.edit_text("⛔ بدون قبول قوانین نمی‌توانی استفاده کنی")

    elif q.data == "img":
        await q.message.reply_text("🖼 متن برای ساخت عکس بفرست")

    elif q.data == "music":
        await q.message.reply_text("🎵 متن برای ساخت موزیک بفرست")


# ================= IMAGE =================
def generate_image(prompt):
    url = f"https://api-inference.huggingface.co/models/{IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    r = requests.post(url, headers=headers, json={"inputs": prompt})

    if r.status_code == 200:
        return r.content
    return None


# ================= MUSIC =================
def generate_music(prompt):
    url = f"https://api-inference.huggingface.co/models/{MUSIC_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    r = requests.post(url, headers=headers, json={"inputs": prompt})

    if r.status_code == 200:
        file = "music.mp3"
        with open(file, "wb") as f:
            f.write(r.content)
        return file

    return None


# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in db["users"]:
        return

    user = db["users"][user_id]

    if user.get("blocked"):
        await update.message.reply_text("⛔ شما مسدود هستید")
        return

    if not user.get("accepted"):
        await update.message.reply_text("اول قوانین را قبول کن ❗")
        return

    # ===== IMAGE =====
    if text.startswith("🖼"):
        prompt = text.replace("🖼", "").strip()
        await update.message.reply_text("⏳ در حال ساخت عکس...")

        img = generate_image(prompt)
        if img:
            await update.message.reply_photo(img)
        else:
            await update.message.reply_text("❌ خطا در ساخت عکس")

    # ===== MUSIC =====
    elif text.startswith("🎵"):
        prompt = text.replace("🎵", "").strip()
        await update.message.reply_text("⏳ در حال ساخت موزیک...")

        file = generate_music(prompt)
        if file:
            await update.message.reply_audio(open(file, "rb"))
        else:
            await update.message.reply_text("❌ خطا در ساخت موزیک")


# ================= APP =================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT, text_handler))

print("Bot is running...")
app.run_polling()
