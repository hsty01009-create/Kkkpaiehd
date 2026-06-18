import os
import google.generativeai as genai
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ======================
# CONFIG
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

CREATOR = "Amir Ali Forouzan"

user_lang = {}
user_accept = {}

# ======================
# LANGUAGES (6 languages)
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
# RULES
# ======================
def rules(lang):
    text = {
        "fa": "📜 قوانین: استفاده فقط با قبول قوانین امکان پذیر است",
        "en": "📜 Rules: You must accept terms",
        "ru": "📜 Правила: принять условия",
        "ar": "📜 القوانين: يجب قبول الشروط",
        "tr": "📜 Kurallar: şartları kabul et",
        "hi": "📜 नियम: उपयोग के लिए स्वीकार करें",
        "es": "📜 Reglas: debes aceptar términos"
    }
    return text.get(lang, text["en"])

def accept_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✔ Accept", callback_data="accept")],
        [InlineKeyboardButton("❌ Reject", callback_data="reject")]
    ])

# ======================
# MAIN MENU
# ======================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 Create Image", callback_data="img")],
        [InlineKeyboardButton("🖊 Edit Image", callback_data="edit")],
        [InlineKeyboardButton("⬇️ Download", callback_data="dl")]
    ])

# ======================
# GEMINI PROMPT GENERATOR
# ======================
def gemini_prompt(prompt):
    model = genai.GenerativeModel("gemini-pro")

    res = model.generate_content(
        f"Create a detailed cinematic AI image prompt:\n{prompt}"
    )

    # چون Gemini عکس نمی‌دهد
    return "https://picsum.photos/512"

# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 Select Language", reply_markup=lang_menu())

# ======================
# CALLBACK
# ======================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # LANGUAGE
    if q.data in ["fa","en","ru","ar","tr","hi","es"]:
        user_lang[uid] = q.data
        await q.message.edit_text(rules(q.data), reply_markup=accept_btn())

    # ACCEPT RULES
    elif q.data == "accept":
        user_accept[uid] = True
        await q.message.edit_text("✅ Welcome!", reply_markup=main_menu())

    elif q.data == "reject":
        await q.message.edit_text("❌ Access denied")

    elif q.data == "img":
        await q.message.reply_text("✍ Send prompt")

    elif q.data == "edit":
        await q.message.reply_text("🖊 Send image + prompt")

# ======================
# TEXT HANDLER
# ======================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    if not user_accept.get(uid):
        await update.message.reply_text("❌ Please accept rules first")
        return

    prompt = update.message.text

    await update.message.reply_text("🎨 Creating image...")

    img = gemini_prompt(prompt)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬇️ Download Image", url=img)]
    ])

    await update.message.reply_photo(
        photo=img,
        caption=f"🎨 Created by {CREATOR}",
        reply_markup=keyboard
    )

# ======================
# RUN BOT
# ======================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("BOT RUNNING 24/7")
app.run_polling()
