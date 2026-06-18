import os
import base64
import uuid
import requests
from collections import defaultdict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")

AI_TXT2IMG = "http://127.0.0.1:7860/sdapi/v1/txt2img"
AI_IMG2IMG = "http://127.0.0.1:7860/sdapi/v1/img2img"

# =========================
# DATA
# =========================
user_lang = {}
user_image = {}
user_mode = {}
user_gallery = defaultdict(list)

# =========================
# MENU
# =========================
def menu(lang):
    if lang == "fa":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎨 ساخت عکس", callback_data="img")],
            [InlineKeyboardButton("✏️ ادیت (اختیاری)", callback_data="edit")],
            [InlineKeyboardButton("🗂 گالری", callback_data="gallery")]
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 Create Image", callback_data="img")],
        [InlineKeyboardButton("✏️ Optional Edit", callback_data="edit")],
        [InlineKeyboardButton("🗂 Gallery", callback_data="gallery")]
    ])

def download_btn(path, lang):
    text = "⬇️ دانلود" if lang == "fa" else "⬇️ Download"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"dl:{path}")]
    ])

# =========================
# AI GENERATE
# =========================
def generate(prompt):
    res = requests.post(AI_TXT2IMG, json={
        "prompt": prompt,
        "steps": 25,
        "width": 512,
        "height": 512
    })

    img = res.json()["images"][0]
    name = f"{uuid.uuid4()}.png"

    with open(name, "wb") as f:
        f.write(base64.b64decode(img))

    return name

# =========================
# AI EDIT
# =========================
def edit(image_path, prompt):
    with open(image_path, "rb") as f:
        img64 = base64.b64encode(f.read()).decode()

    res = requests.post(AI_IMG2IMG, json={
        "init_images": [img64],
        "prompt": prompt,
        "steps": 25,
        "denoising_strength": 0.7
    })

    img = res.json()["images"][0]
    name = f"edit_{uuid.uuid4()}.png"

    with open(name, "wb") as f:
        f.write(base64.b64decode(img))

    return name

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="fa")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="en")]
    ])

    await update.message.reply_text("🌐 Choose language", reply_markup=keyboard)

# =========================
# CALLBACK
# =========================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    # LANGUAGE
    if q.data == "fa":
        user_lang[uid] = "fa"
        await q.message.edit_text("✅ فارسی فعال شد", reply_markup=menu("fa"))

    elif q.data == "en":
        user_lang[uid] = "en"
        await q.message.edit_text("✅ English enabled", reply_markup=menu("en"))

    # IMAGE MODE
    elif q.data == "img":
        user_mode[uid] = "img"
        await q.message.reply_text("✍ متن عکس را بفرست")

    # OPTIONAL EDIT MODE
    elif q.data == "edit":
        user_mode[uid] = "edit"
        await q.message.reply_text("📸 اگر عکس داری بفرست، اگر نداری فقط متن بده")

    # GALLERY
    elif q.data == "gallery":
        imgs = user_gallery.get(uid, [])

        if not imgs:
            await q.message.reply_text("🗂 خالی است")
            return

        for i in imgs[-5:]:
            await q.message.reply_photo(open(i, "rb"))

    # DOWNLOAD
    elif q.data.startswith("dl:"):
        path = q.data.split("dl:")[1]
        await q.message.reply_document(open(path, "rb"))

# =========================
# PHOTO HANDLER
# =========================
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    file = await update.message.photo[-1].get_file()
    path = f"{uid}.jpg"

    await file.download_to_drive(path)

    user_image[uid] = path

    lang = user_lang.get(uid, "en")
    text = "📸 عکس ذخیره شد (حالا می‌تونی ادیت کنی)" if lang == "fa" else "📸 Image saved (you can edit now)"

    await update.message.reply_text(text)

# =========================
# TEXT HANDLER (SMART LOGIC)
# =========================
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    txt = update.message.text

    lang = user_lang.get(uid, "en")

    msg = await update.message.reply_text("⏳ processing...")

    try:
        # اگر عکس دارد → ادیت
        if user_mode.get(uid) == "edit" and uid in user_image:
            file = edit(user_image[uid], txt)

        # اگر عکس ندارد → ساخت عکس
        else:
            file = generate(txt)

        user_gallery[uid].append(file)

        await msg.delete()

        caption = "🎨 ساخته شد" if lang == "fa" else "🎨 Generated"

        await update.message.reply_photo(
            photo=open(file, "rb"),
            caption=caption,
            reply_markup=download_btn(file, lang)
        )

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{e}")

# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

    print("🚀 SMART BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
