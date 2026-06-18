import os
import json
import requests
import asyncio
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

MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
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
        "real": "realistic, ultra detailed, 4k, sharp focus",
        "anime": "anime style, high quality, detailed",
        "cinematic": "cinematic lighting, dramatic film look",
        "3d": "3d render, octane render, ultra detailed"
    }
    return f"{text}, {styles.get(style, 'realistic')}"


# ================= BUTTONS =================
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


def download_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 دانلود عکس", callback_data="download_img")]
    ])


# ================= PROGRESS =================
async def fake_progress(msg):
    p = 0
    while p < 90:
        p += 10
        try:
            await msg.edit_text(f"⏳ در حال ساخت... {p}%")
        except:
            pass
        await asyncio.sleep(0.4)


# ================= MULTI IMAGE =================
def generate_images(prompt, style="real", count=4):
    final_prompt = build_prompt(style, prompt)

    url = f"https://api-inference.huggingface.co/models/{MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    images = []

    for i in range(count):
        r = requests.post(
            url,
            headers=headers,
            json={"inputs": final_prompt, "options": {"wait_for_model": True}},
            timeout=120
        )

        if r.status_code == 200:
            file = f"img_{i}.jpg"
            with open(file, "wb") as f:
                f.write(r.content)
            images.append(file)

    return images


# ================= MUSIC =================
def generate_music(prompt):
    url = f"https://api-inference.huggingface.co/models/{MUSIC_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    r = requests.post(
        url,
        headers=headers,
        json={"inputs": prompt, "parameters": {"duration": 8}},
        timeout=120
    )

    if r.status_code == 200:
        file = "music.mp3"
        with open(file, "wb") as f:
            f.write(r.content)
        return file

    return None


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in db["users"]:
        db["users"][user_id] = {
            "accepted": False,
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
        db["users"][user_id]["accepted"] = True
        save_db(db)
        await q.message.edit_text("✅ خوش آمدید", reply_markup=menu_kb())

    elif q.data == "reject":
        await q.message.edit_text("⛔ دسترسی بسته شد")

    elif q.data == "img":
        await q.message.reply_text("🖼 متن برای ساخت عکس بفرست")

    elif q.data == "music":
        await q.message.reply_text("🎵 متن برای موزیک بفرست")

    elif q.data == "download_img":
        await q.message.reply_document(open("img_0.jpg", "rb"))


# ================= TEXT =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in db["users"]:
        return

    if not db["users"][user_id]["accepted"]:
        await update.message.reply_text("❗ اول قوانین را قبول کن")
        return

    user = db["users"][user_id]

    # ===== IMAGE =====
    if text.startswith("🖼"):
        prompt = text.replace("🖼", "").strip()

        msg = await update.message.reply_text("⏳ شروع ساخت... 0%")

        await fake_progress(msg)

        images = generate_images(prompt, user.get("style", "real"), count=4)

        if images:
            await msg.delete()

            for img in images:
                await update.message.reply_photo(
                    photo=open(img, "rb"),
                    caption="🖼 HD Image"
                )
        else:
            await msg.edit_text("❌ خطا در ساخت تصویر")

    # ===== MUSIC =====
    elif text.startswith("🎵"):
        prompt = text.replace("🎵", "").strip()

        msg = await update.message.reply_text("⏳ در حال ساخت موزیک...")

        file = generate_music(prompt)

        if file:
            await msg.delete()
            await update.message.reply_audio(open(file, "rb"))
        else:
            await msg.edit_text("❌ خطا")


# ================= APP =================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT, text_handler))

print("Bot running...")
app.run_polling()
