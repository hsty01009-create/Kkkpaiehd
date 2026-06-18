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


# ================= STYLE =================
def build_prompt(style, text):
    styles = {
        "real": "realistic, ultra detailed, 4k",
        "anime": "anime style, high quality",
        "cinematic": "cinematic lighting, dramatic",
        "3d": "3d render, ultra detailed"
    }
    return f"{text}, {styles.get(style, 'realistic')}"


# ================= BUTTONS =================
def agree_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ قبول قوانین", callback_data="accept")],
        [InlineKeyboardButton("❌ رد", callback_data="reject")]
    ])


def lang_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="fa")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="en")]
    ])


def style_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 Real", callback_data="real")],
        [InlineKeyboardButton("🎬 Cinematic", callback_data="cinematic")],
        [InlineKeyboardButton("🖌 Anime", callback_data="anime")],
        [InlineKeyboardButton("🧊 3D", callback_data="3d")]
    ])


def menu_kb():
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
            "lang": "fa",
            "style": "real"
        }
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
        await q.message.edit_text("🌍 انتخاب زبان:", reply_markup=lang_kb())

    elif q.data == "reject":
        await q.message.edit_text("⛔ دسترسی بسته شد")

    elif q.data in ["fa", "en"]:
        db["users"][user_id]["accepted"] = True
        db["users"][user_id]["lang"] = q.data
        save_db(db)

        await q.message.edit_text("🎛 منو:", reply_markup=menu_kb())

    elif q.data in ["real", "anime", "cinematic", "3d"]:
        db["users"][user_id]["style"] = q.data
        save_db(db)
        await q.message.reply_text("✅ سبک انتخاب شد")

    elif q.data == "img":
        await q.message.reply_text("🖼 متن + سبک را ارسال کن")

    elif q.data == "music":
        await q.message.reply_text("🎵 متن موزیک را ارسال کن")


# ================= IMAGE =================
def generate_image(prompt, style):
    final_prompt = build_prompt(style, prompt)

    url = f"https://api-inference.huggingface.co/models/{IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    r = requests.post(
        url,
        headers=headers,
        json={"inputs": final_prompt, "options": {"wait_for_model": True}},
        timeout=120
    )

    return r.content if r.status_code == 200 else None


# ================= MUSIC (5 MIN LOOP) =================
def generate_music(prompt):
    url = f"https://api-inference.huggingface.co/models/{MUSIC_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    audio = []

    for _ in range(8):  # حدود چند دقیقه
        r = requests.post(
            url,
            headers=headers,
            json={"inputs": prompt, "parameters": {"duration": 8}},
            timeout=120
        )

        if r.status_code == 200:
            audio.append(r.content)

    file = "music.mp3"
    with open(file, "wb") as f:
        for a in audio:
            f.write(a)

    return file


# ================= TEXT =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in db["users"]:
        return

    user = db["users"][user_id]

    if not user.get("accepted"):
        await update.message.reply_text("❗ اول قوانین را قبول کن")
        return

    # ===== IMAGE =====
    if text.startswith("🖼"):
        prompt = text.replace("🖼", "").strip()
        await update.message.reply_text("⏳ در حال ساخت عکس...")

        img = generate_image(prompt, user.get("style", "real"))

        if img:
            await update.message.reply_photo(img)
        else:
            await update.message.reply_text("❌ خطا")

    # ===== MUSIC =====
    elif text.startswith("🎵"):
        prompt = text.replace("🎵", "").strip()
        await update.message.reply_text("⏳ در حال ساخت موزیک...")

        file = generate_music(prompt)

        await update.message.reply_audio(open(file, "rb"))


# ================= APP =================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT, text_handler))

print("Bot running...")
app.run_polling()
