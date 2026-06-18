import os
import uuid
import replicate
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
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# =========================
# DATA
# =========================
user_lang = {}
user_gallery = defaultdict(list)

# =========================
# MENU
# =========================
def lang_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="fa")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="en")]
    ])

def main_menu(lang):
    if lang == "fa":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎨 ساخت عکس", callback_data="img")],
            [InlineKeyboardButton("🗂 گالری", callback_data="gallery")]
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 Create Image", callback_data="img")],
        [InlineKeyboardButton("🗂 Gallery", callback_data="gallery")]
    ])

def download_btn(file_url, lang):
    text = "⬇️ دانلود" if lang == "fa" else "⬇️ Download"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"dl:{file_url}")]
    ])

# =========================
# AI IMAGE (REPLICATE)
# =========================
def generate_image(prompt):
    output = replicate.run(
        "black-forest-labs/flux-2-pro",
        input={
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "output_format": "png"
        }
    )
    return output[0]

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 Choose Language",
        reply_markup=lang_menu()
    )

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
        await q.message.edit_text("✅ فارسی فعال شد", reply_markup=main_menu("fa"))

    elif q.data == "en":
        user_lang[uid] = "en"
        await q.message.edit_text("✅ English enabled", reply_markup=main_menu("en"))

    # CREATE IMAGE MODE
    elif q.data == "img":
        await q.message.reply_text("✍ متن عکس را ارسال کن / Send prompt")

    # GALLERY
    elif q.data == "gallery":
        imgs = user_gallery.get(uid, [])
        if not imgs:
            await q.message.reply_text("🗂 خالی است / Empty")
            return

        for img in imgs[-5:]:
            await q.message.reply_photo(img)

    # DOWNLOAD
    elif q.data.startswith("dl:"):
        file_url = q.data.split("dl:")[1]
        await q.message.reply_document(file_url)

# =========================
# TEXT HANDLER (CREATE IMAGE)
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    prompt = update.message.text

    lang = user_lang.get(uid, "en")

    msg = await update.message.reply_text("⏳ generating...")

    try:
        image_url = generate_image(prompt)

        user_gallery[uid].append(image_url)

        await msg.delete()

        caption = "🎨 ساخته شد" if lang == "fa" else "🎨 Generated"

        await update.message.reply_photo(
            photo=image_url,
            caption=caption,
            reply_markup=download_btn(image_url, lang)
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🚀 BOT RUNNING ON RAILWAY")
    app.run_polling()

if __name__ == "__main__":
    main()
