import os
import json
import time
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# ================= TOKENS =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

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


def quality_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Fast", callback_data="q_fast")],
        [InlineKeyboardButton("🔥 HD", callback_data="q_hd")],
        [InlineKeyboardButton("💎 Ultra HD", callback_data="q_ultra")]
    ])


def music_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 Short", callback_data="m_short")],
        [InlineKeyboardButton("🎶 Normal", callback_data="m_normal")],
        [InlineKeyboardButton("🎧 Long", callback_data="m_long")]
    ])


def download_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 دانلود فایل", callback_data="download")]
    ])


# ================= PROGRESS =================
async def loading(msg, start_time):
    dots = ["⏳", "⏳⏳", "⏳⏳⏳"]

    for i in range(6):
        elapsed = round(time.time() - start_time, 1)
        try:
            await msg.edit_text(f"{dots[i % 3]} در حال ساخت...\n⏱ {elapsed} ثانیه")
        except:
            pass
        await asyncio.sleep(0.8)


# ================= IMAGE =================
def generate_image(prompt, quality):
    start = time.time()

    quality_prompt = {
        "q_fast": "low quality, fast render",
        "q_hd": "high quality, 4k, ultra detailed",
        "q_ultra": "ultra realistic, 8k, cinematic lighting, masterpiece"
    }

    final_prompt = f"{prompt}, {quality_prompt.get(quality, 'high quality')}"

    url = f"https://api-inference.huggingface.co/models/{IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        r = requests.post(
            url,
            headers=headers,
            json={"inputs": final_prompt, "options": {"wait_for_model": True}},
            timeout=180
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
def generate_music(prompt, mode):
    start = time.time()

    duration_map = {
        "m_short": 4,
        "m_normal": 8,
        "m_long": 12
    }

    url = f"https://api-inference.huggingface.co/models/{MUSIC_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        r = requests.post(
            url,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {"duration": duration_map.get(mode, 8)}
            },
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

    await update.message.reply_text(
        "📜 قوانین ربات\n"
        "👨‍💼 سازنده: امیر علی فروزان اصل\n\n"
        "آیا قوانین را قبول می‌کنی؟",
        reply_markup=agree_kb()
    )


# ================= BUTTONS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = str(q.from_user.id)

    if q.data == "accept":
        db["users"][user_id]["accepted"] = True
        save_db(db)
        await q.message.edit_text("✅ منو اصلی", reply_markup=menu_kb())

    elif q.data == "reject":
        await q.message.edit_text("⛔ دسترسی بسته شد")

    elif q.data == "img":
        await q.message.reply_text("🖼 کیفیت عکس را انتخاب کن:", reply_markup=quality_kb())

    elif q.data == "music":
        await q.message.reply_text("🎵 مدت موزیک را انتخاب کن:", reply_markup=music_kb())

    elif q.data == "download":
        await q.message.reply_document(open("output.jpg", "rb"))


# ================= MEMORY =================
user_state = {}


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

        quality = user_state.get(user_id, {}).get("quality", "q_hd")

        msg = await update.message.reply_text("⏳ شروع ساخت...")

        await loading(msg, time.time())

        file, sec = generate_image(prompt, quality)

        if file:
            os.rename(file, "output.jpg")

            await msg.delete()

            await update.message.reply_photo(
                photo=open("output.jpg", "rb"),
                caption=f"🖼 آماده شد\n⏱ زمان: {sec} ثانیه\n👨‍💼 امیر علی فروزان اصل",
                reply_markup=download_kb()
            )
        else:
            await msg.edit_text("❌ خطا در ساخت عکس")

    # ================= MUSIC =================
    elif text.startswith("🎵"):
        prompt = text.replace("🎵", "").strip()

        mode = user_state.get(user_id, {}).get("music", "m_normal")

        msg = await update.message.reply_text("⏳ در حال ساخت موزیک...")

        file, sec = generate_music(prompt, mode)

        if file:
            await msg.delete()

            await update.message.reply_audio(
                audio=open(file, "rb"),
                caption=f"🎵 آماده شد\n⏱ زمان: {sec} ثانیه\n👨‍💼 امیر علی فروزان اصل"
            )
        else:
            await msg.edit_text("❌ خطا")


# ================= CALLBACK =================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = str(q.from_user.id)

    if q.data in ["q_fast", "q_hd", "q_ultra"]:
        user_state.setdefault(user_id, {})["quality"] = q.data
        await q.message.reply_text("✅ کیفیت انتخاب شد\n🖼 حالا متن عکس را بفرست")

    elif q.data in ["m_short", "m_normal", "m_long"]:
        user_state.setdefault(user_id, {})["music"] = q.data
        await q.message.reply_text("✅ حالت انتخاب شد\n🎵 حالا متن موزیک را بفرست")


# ================= RUN =================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters.TEXT, text_handler))

print("Bot running...")
app.run_polling()
