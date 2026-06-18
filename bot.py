import os
import json
import time
import asyncio
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


# ================= DB =================
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


# ================= UI =================
def agree_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ قبول قوانین", callback_data="accept")],
        [InlineKeyboardButton("❌ رد", callback_data="reject")]
    ])


def menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 ساخت عکس", callback_data="img")],
        [InlineKeyboardButton("🎵 ساخت موزیک", callback_data="music")]
    ])


# ================= LOADING =================
async def loading(msg, start_time):
    dots = ["⏳", "⏳⏳", "⏳⏳⏳"]

    for i in range(6):
        elapsed = round(time.time() - start_time, 1)
        try:
            await msg.edit_text(f"{dots[i % 3]} در حال ساخت...\n⏱ {elapsed} ثانیه")
        except:
            pass
        await asyncio.sleep(1)


# ================= IMAGE =================
def generate_image(prompt):
    start = time.time()

    url = f"https://api-inference.huggingface.co/models/{IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        r = requests.post(
            url,
            headers=headers,
            json={"inputs": prompt, "options": {"wait_for_model": True}},
            timeout=120
        )

        duration = round(time.time() - start, 2)

        if r.status_code == 200:
            file = "image.jpg"
            with open(file, "wb") as f:
                f.write(r.content)
            return file, duration

    except:
        pass

    return None, 0


# ================= MUSIC =================
def generate_music(prompt):
    start = time.time()

    url = f"https://api-inference.huggingface.co/models/{MUSIC_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        r = requests.post(
            url,
            headers=headers,
            json={"inputs": prompt, "parameters": {"duration": 8}},
            timeout=180
        )

        duration = round(time.time() - start, 2)

        if r.status_code == 200:
            file = "music.mp3"
            with open(file, "wb") as f:
                f.write(r.content)
            return file, duration

    except:
        pass

    return None, 0


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in db["users"]:
        db["users"][user_id] = {"accepted": False}
        save_db(db)

    text = (
        "📜 قوانین ربات\n\n"
        "👨‍💼 سازنده: امیر علی فروزان اصل\n\n"
        "⚠️ استفاده از ربات مسئولیت کاربر است\n"
        "⚠️ محتوای تولیدی ممکن است خطا داشته باشد\n\n"
        "آیا قوانین را قبول می‌کنید؟"
    )

    await update.message.reply_text(text, reply_markup=agree_kb())


# ================= BUTTONS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = str(q.from_user.id)

    if q.data == "accept":
        db["users"][user_id]["accepted"] = True
        save_db(db)
        await q.message.edit_text("✅ خوش آمدید", reply_markup=menu_kb())

    elif q.data == "reject":
        await q.message.edit_text("⛔ دسترسی بسته شد")

    elif q.data == "img":
        await q.message.reply_text("🖼 متن برای ساخت عکس بفرست")

    elif q.data == "music":
        await q.message.reply_text("🎵 متن برای ساخت موزیک بفرست")


# ================= TEXT =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in db["users"]:
        return

    if not db["users"][user_id]["accepted"]:
        await update.message.reply_text("❗ اول قوانین را قبول کن")
        return

    # ================= IMAGE =================
    if text.startswith("🖼"):
        prompt = text.replace("🖼", "").strip()

        start_time = time.time()
        msg = await update.message.reply_text("⏳ شروع ساخت...")

        task = asyncio.create_task(loading(msg, start_time))

        file, duration = generate_image(prompt)

        if file:
            await msg.delete()
            await update.message.reply_photo(
                photo=open(file, "rb"),
                caption=f"🖼 عکس آماده شد\n⏱ زمان: {duration} ثانیه\n👨‍💼 امیر علی فروزان اصل"
            )
        else:
            await msg.edit_text("❌ خطا در ساخت عکس")

    # ================= MUSIC =================
    elif text.startswith("🎵"):
        prompt = text.replace("🎵", "").strip()

        msg = await update.message.reply_text("⏳ در حال ساخت موزیک...")

        file, duration = generate_music(prompt)

        if file:
            await msg.delete()
            await update.message.reply_audio(
                audio=open(file, "rb"),
                caption=f"🎵 موزیک آماده شد\n⏱ زمان: {duration} ثانیه\n👨‍💼 امیر علی فروزان اصل"
            )
        else:
            await msg.edit_text("❌ خطا در ساخت موزیک")


# ================= RUN =================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT, text_handler))

print("Bot is running...")
app.run_polling()
