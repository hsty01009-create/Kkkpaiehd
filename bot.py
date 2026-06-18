import os
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
# TOKENS
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# =========================
# USER DATA
# =========================
accepted = set()
user_lang = {}
user_mode = {}
user_gallery = defaultdict(list)
user_image = {}

# =========================
# RULES
# =========================
RULES = """
📜 RULES

👤 Creator: Amir Ali Forouzan

✔ Accept rules to use bot
✔ Free AI generation
✔ No abuse allowed
"""

# =========================
# MENUS
# =========================
def lang_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="fa")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="en")]
    ])

def main_menu(lang="en"):
    if lang == "fa":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎨 ساخت عکس", callback_data="img")],
            [InlineKeyboardButton("✏️ ادیت عکس", callback_data="edit")],
            [InlineKeyboardButton("🗂 گالری", callback_data="gallery")]
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 Create Image", callback_data="img")],
        [InlineKeyboardButton("✏️ Edit Image", callback_data="edit")],
        [InlineKeyboardButton("🗂 Gallery", callback_data="gallery")]
    ])

# =========================
# HF IMAGE GENERATION (FREE)
# =========================
def generate(prompt):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    response = requests.post(
        url,
        headers=headers,
        json={"inputs": prompt}
    )

    return response.content

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    if uid not in accepted:
        await update.message.reply_text(
            RULES,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Accept", callback_data="accept")]
            ])
        )
        return

    await update.message.reply_text("🌐 Choose language:", reply_markup=lang_menu())

# =========================
# CALLBACKS
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    # ACCEPT RULES
    if q.data == "accept":
        accepted.add(uid)
        await q.message.edit_text("✅ Accepted!", reply_markup=lang_menu())

    # LANGUAGE
    elif q.data == "fa":
        user_lang[uid] = "fa"
        await q.message.edit_text("✅ فارسی فعال شد", reply_markup=main_menu("fa"))

    elif q.data == "en":
        user_lang[uid] = "en"
        await q.message.edit_text("✅ English enabled", reply_markup=main_menu("en"))

    # MODE
    elif q.data == "img":
        user_mode[uid] = "img"
        await q.message.reply_text("✍ Send prompt")

    elif q.data == "edit":
        user_mode[uid] = "edit"
        await q.message.reply_text("📸 Send image first")

    elif q.data == "gallery":
        imgs = user_gallery.get(uid, [])

        if not imgs:
            await q.message.reply_text("🗂 Empty gallery")
            return

        for img in imgs[-5:]:
            await q.message.reply_photo(img)

# =========================
# TEXT HANDLER
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if uid not in accepted:
        await update.message.reply_text("❌ Accept rules first")
        return

    msg = await update.message.reply_text("⏳ generating...")

    try:
        image = generate(text)

        user_gallery[uid].append(image)

        await msg.delete()

        await update.message.reply_photo(
            photo=image,
            caption="🎨 Generated Free AI Bot"
        )

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{e}")

# =========================
# PHOTO HANDLER
# =========================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    file = await update.message.photo[-1].get_file()
    path = f"{uid}.jpg"
    await file.download_to_drive(path)

    user_image[uid] = path
    user_gallery[uid].append(path)

    await update.message.reply_text("📸 Saved to gallery")

# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🚀 FREE BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
