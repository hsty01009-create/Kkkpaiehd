import os
import asyncio
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
# TOKENS
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# =========================
# DATA STORAGE
# =========================
accepted_users = set()
user_lang = {}
user_mode = {}
user_style = {}
user_gallery = defaultdict(list)
user_image = {}

# =========================
# RULES
# =========================
RULES = """
📜 TERMS & CONDITIONS

👤 Creator: Amir Ali Forouzan

✔ You must accept rules to use bot
✔ No abuse allowed
✔ AI may take time to generate images
"""

# =========================
# MAIN MENU
# =========================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 Create Image", callback_data="img")],
        [InlineKeyboardButton("✏️ Edit Image", callback_data="edit")],
        [InlineKeyboardButton("🎭 Style", callback_data="style")],
        [InlineKeyboardButton("🗂 Gallery", callback_data="gallery")]
    ])

# =========================
# STYLE MENU
# =========================
def style_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Real", callback_data="s_real")],
        [InlineKeyboardButton("🎬 Cinematic", callback_data="s_cine")],
        [InlineKeyboardButton("🎨 Anime", callback_data="s_anime")],
        [InlineKeyboardButton("🧊 3D", callback_data="s_3d")]
    ])

STYLE_MAP = {
    "real": "realistic, ultra detailed",
    "cine": "cinematic lighting, film style",
    "anime": "anime style, vibrant colors",
    "3d": "3D render, ultra quality"
}

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    if uid not in accepted_users:
        await update.message.reply_text(
            RULES,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Accept Rules", callback_data="accept")]
            ])
        )
        return

    await update.message.reply_text("🚀 Welcome!", reply_markup=menu())

# =========================
# GENERATE IMAGE
# =========================
def generate(prompt):
    return client.run(
        "black-forest-labs/flux-schnell",
        input={
            "prompt": prompt,
            "aspect_ratio": "1:1"
        }
    )

# =========================
# EDIT IMAGE
# =========================
def edit(image_path, prompt):
    return client.run(
        "black-forest-labs/flux-kontext-pro",
        input={
            "image": open(image_path, "rb"),
            "prompt": prompt
        }
    )

# =========================
# CALLBACKS
# =========================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    # ACCEPT RULES
    if q.data == "accept":
        accepted_users.add(uid)
        await q.message.edit_text("✅ Rules accepted!", reply_markup=menu())

    # MODE
    elif q.data == "img":
        user_mode[uid] = "img"
        await q.message.reply_text("✍ Send prompt")

    elif q.data == "edit":
        user_mode[uid] = "edit"
        await q.message.reply_text("📸 Send image first")

    # STYLE
    elif q.data == "style":
        await q.message.reply_text("🎭 Choose style:", reply_markup=style_menu())

    elif q.data.startswith("s_"):
        style = q.data.replace("s_", "")
        user_style[uid] = STYLE_MAP[style]
        await q.message.reply_text(f"✅ Style set: {style}")

    # GALLERY
    elif q.data == "gallery":
        images = user_gallery[uid]

        if not images:
            await q.message.reply_text("🗂 Gallery empty")
            return

        for img in images[-5:]:
            await q.message.reply_photo(img)

# =========================
# TEXT HANDLER
# =========================
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if uid not in accepted_users:
        await update.message.reply_text("❌ First accept rules")
        return

    style = user_style.get(uid, "")
    prompt = f"{text}, {style}" if style else text

    msg = await update.message.reply_text("⏳ generating...")

    loop = asyncio.get_event_loop()

    try:
        result = await loop.run_in_executor(None, generate, prompt)

        await msg.delete()

        user_gallery[uid].append(result)

        await update.message.reply_photo(
            photo=result,
            caption="🎨 Created by Amir Ali Forouzan Bot"
        )

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{e}")

# =========================
# PHOTO HANDLER
# =========================
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    file = await update.message.photo[-1].get_file()
    path = f"{uid}.jpg"
    await file.download_to_drive(path)

    user_image[uid] = path
    user_gallery[uid].append(path)

    await update.message.reply_text("📸 Image saved")

# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    app.add_handler(MessageHandler(filters.PHOTO, photo))

    print("🚀 BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
