import os
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ======================
# CONFIG
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

CREATOR = "Amir Ali Forouzan"

# ======================
# LANGUAGE MAP
# ======================
LANG_MAP = {
    "fa": "Persian",
    "en": "English",
    "ru": "Russian",
    "ar": "Arabic",
    "tr": "Turkish",
    "hi": "Hindi",
    "es": "Spanish"
}

# ======================
# USERS DATA
# ======================
user_accept = {}
user_lang = {}
user_mode = {}

# ======================
# LANGUAGE MENU
# ======================
def lang_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="fa")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="en")],
        [InlineKeyboardButton("🇷🇺 Russian", callback_data="ru")],
        [InlineKeyboardButton("🇸🇦 Arabic", callback_data="ar")],
        [InlineKeyboardButton("🇹🇷 Turkish", callback_data="tr")],
        [InlineKeyboardButton("🇮🇳 Hindi", callback_data="hi")],
        [InlineKeyboardButton("🇪🇸 Spanish", callback_data="es")]
    ])

# ======================
# RULES BUTTON
# ======================
def rules():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✔ Accept", callback_data="accept")],
        [InlineKeyboardButton("❌ Reject", callback_data="reject")]
    ])

# ======================
# MAIN MENU
# ======================
def glass_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Chat AI", callback_data="chat")],
        [InlineKeyboardButton("🎨 Create Image", callback_data="img")],
        [InlineKeyboardButton("🖊 Edit Image", callback_data="edit")],
        [InlineKeyboardButton("ℹ About", callback_data="about")]
    ])

# ======================
# AI FUNCTION
# ======================
def ask_ai(text, lang="English"):
    try:
        prompt = f"""
You must reply ONLY in {lang}.
User message: {text}
"""
        return model.generate_content(prompt).text
    except:
        return "❌ AI Error"

# ======================
# FAKE IMAGE
# ======================
def fake_image():
    return "https://picsum.photos/512"

# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Select Language",
        reply_markup=lang_menu()
    )

# ======================
# CALLBACK HANDLER
# ======================
async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # LANGUAGE SELECT
    if q.data in LANG_MAP:
        user_lang[uid] = q.data
        await q.message.edit_text(
            "📜 Please accept rules to continue:",
            reply_markup=rules()
        )
        return

    # ACCEPT RULES
    if q.data == "accept":
        user_accept[uid] = True
        await q.message.edit_text("💎 Access Granted", reply_markup=glass_menu())
        return

    # REJECT
    if q.data == "reject":
        await q.message.edit_text("❌ Access Denied")
        return

    # BLOCK IF NOT ACCEPTED
    if not user_accept.get(uid):
        return

    # MENU OPTIONS
    if q.data == "chat":
        user_mode[uid] = "chat"
        await q.message.reply_text("💬 Send message")

    elif q.data == "img":
        user_mode[uid] = "img"
        await q.message.reply_text("🎨 Send prompt")

    elif q.data == "edit":
        user_mode[uid] = "edit"
        await q.message.reply_text("🖊 Send text")

    elif q.data == "about":
        await q.message.reply_text(f"👤 Creator: {CREATOR}")

# ======================
# TEXT HANDLER
# ======================
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if not user_accept.get(uid):
        await update.message.reply_text("❌ You must accept rules first")
        return

    mode = user_mode.get(uid, "chat")
    lang_code = user_lang.get(uid, "en")
    lang = LANG_MAP.get(lang_code, "English")

    # CHAT AI
    if mode == "chat":
        await update.message.reply_text("🤖 Thinking...")
        ans = ask_ai(text, lang)
        await update.message.reply_text(ans)

    # IMAGE
    elif mode == "img":
        msg = "🎨 Creating image..." if lang_code == "en" else "🎨 در حال ساخت تصویر..."
        await update.message.reply_text(msg)
        img = fake_image()
        await update.message.reply_photo(
            photo=img,
            caption=f"Prompt: {text}\n👤 {CREATOR}"
        )

    # EDIT
    elif mode == "edit":
        msg = "🖊 Image edited (demo mode)" if lang_code == "en" else "🖊 تصویر ویرایش شد (دمو)"
        await update.message.reply_text(f"{msg}\n{text}\n👤 {CREATOR}")

# ======================
# RUN BOT
# ======================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(cb))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

print("💎 GLASS BOT RUNNING 24/7")
app.run_polling()
