import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from database import *
from texts import LANGS, welcome
from rules import RULES
from sticker import make_sticker
from image_tools import edit_image

TOKEN = "YOUR_BOT_TOKEN"

user_state = {}

# ---------------- AI IMAGE ----------------
def generate_ai(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}"

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await add_user(uid)

    keyboard = [
        [InlineKeyboardButton("🌍 Language", callback_data="lang")],
        [InlineKeyboardButton("💰 Coins", callback_data="coins")],
        [InlineKeyboardButton("📜 Rules", callback_data="rules")],
        [InlineKeyboardButton("👥 Invite", callback_data="invite")],
        [InlineKeyboardButton("🧸 Sticker", callback_data="sticker")],
        [InlineKeyboardButton("🎨 Edit", callback_data="edit")],
        [InlineKeyboardButton("🎨 AI Image", callback_data="ai")]
    ]

    await update.message.reply_text(
        welcome("fa", 100),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- BUTTONS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    user = await get_user(uid)

    # حذف دکمه‌ها بعد کلیک
    await q.message.edit_reply_markup(None)

    # RULES
    if q.data == "rules":
        await q.message.reply_text(RULES)

    # COINS
    elif q.data == "coins":
        await q.message.reply_text(f"💰 Coins: {user[1]}")

    # INVITE
    elif q.data == "invite":
        link = f"https://t.me/YOURBOT?start={uid}"
        await q.message.reply_text(f"🔗 {link}\n🎁 200 coins")

    # LANG
    elif q.data == "lang":
        kb = [[InlineKeyboardButton(v, callback_data=f"set_{k}")] for k,v in LANGS.items()]
        await q.message.reply_text("🌍 Select:", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("set_"):
        lang = q.data.split("_")[1]
        await update_lang(uid, lang)
        await q.message.reply_text("✅ Done")

    # MODES
    elif q.data == "sticker":
        user_state[uid] = "sticker"
        await q.message.reply_text("📸 Send photo")

    elif q.data == "edit":
        user_state[uid] = "edit"
        await q.message.reply_text("📸 Send photo")

    elif q.data == "ai":
        user_state[uid] = "ai"
        await q.message.reply_text("✍️ Send prompt")

# ---------------- PHOTO ----------------
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    file = await update.message.photo[-1].get_file()
    path = f"{uid}.jpg"
    await file.download_to_drive(path)

    if user_state.get(uid) == "sticker":
        out = make_sticker(path)
        await update.message.reply_sticker(sticker=open(out, "rb"))

    elif user_state.get(uid) == "edit":
        out = edit_image(path)
        await update.message.reply_photo(photo=open(out, "rb"))

# ---------------- TEXT (AI) ----------------
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if user_state.get(uid) == "ai":
        url = generate_ai(update.message.text)
        await update.message.reply_photo(photo=url)

# ---------------- RUN ----------------
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO, photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

app.run_polling()
