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

model = genai.GenerativeModel("gemini-3.5-flash")

CREATOR = "Amir Ali Forouzan"

# ======================
# USERS DATA
# ======================
user_accept = {}
user_lang = {}
user_mode = {}

# ======================
# 🌍 LANGUAGE MENU
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
# 📜 RULES BUTTON (GLASS)
# ======================
def rules():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✔ 𝗔𝗰𝗰𝗲𝗽𝘁", callback_data="accept")],
        [InlineKeyboardButton("❌ 𝗥𝗲𝗷𝗲𝗰𝘁", callback_data="reject")]
    ])

# ======================
# 🎛 GLASS MENU
# ======================
def glass_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 𝗖𝗵𝗮𝘁 𝗔𝗜", callback_data="chat")],
        [InlineKeyboardButton("🎨 𝗖𝗿𝗲𝗮𝘁𝗲 𝗜𝗺𝗮𝗴𝗲", callback_data="img")],
        [InlineKeyboardButton("🖊 𝗘𝗱𝗶𝘁 𝗜𝗺𝗮𝗴𝗲", callback_data="edit")],
        [InlineKeyboardButton("ℹ 𝗔𝗯𝗼𝘂𝘁", callback_data="about")]
    ])

# ======================
# 🤖 GEMINI AI
# ======================
def ask_ai(text):
    try:
        return model.generate_content(text).text
    except:
        return "❌ AI Error"

# ======================
# 🎨 FAKE IMAGE (NO API)
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

    # 🌍 language select
    if q.data in ["fa","en","ru","ar","tr","hi","es"]:
        user_lang[uid] = q.data
        await q.message.edit_text(
            "📜 Please accept rules to continue:",
            reply_markup=rules()
        )

    # ✔ ACCEPT RULES
    elif q.data == "accept":
        user_accept[uid] = True
        await q.message.edit_text("💎 Access Granted", reply_markup=glass_menu())

    # ❌ REJECT
    elif q.data == "reject":
        await q.message.edit_text("❌ Access Denied")

    # 🚫 block if not accepted
    if not user_accept.get(uid):
        return

    # 🤖 CHAT MODE
    if q.data == "chat":
        user_mode[uid] = "chat"
        await q.message.reply_text("💬 Send message")

    # 🎨 CREATE IMAGE
    elif q.data == "img":
        user_mode[uid] = "img"
        await q.message.reply_text("🎨 Send prompt")

    # 🖊 EDIT IMAGE
    elif q.data == "edit":
        user_mode[uid] = "edit"
        await q.message.reply_text("🖊 Send image + caption")

    # ℹ ABOUT
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

    mode = user_mode.get(uid)

    # 🤖 CHAT AI
    if mode == "chat":
        await update.message.reply_text("🤖 Thinking...")
        ans = ask_ai(text)
        await update.message.reply_text(ans)

    # 🎨 CREATE IMAGE (FAKE)
    elif mode == "img":
        await update.message.reply_text("🎨 Creating image...")
        img = fake_image()
        await update.message.reply_photo(
            photo=img,
            caption=f"🎨 AI Image (Demo)\nPrompt: {text}\n👤 {CREATOR}"
        )

    # 🖊 EDIT IMAGE (DEMO)
    elif mode == "edit":
        await update.message.reply_text(
            f"🖊 Image edited (demo mode)\nText: {text}\n👤 {CREATOR}"
        )

# ======================
# RUN BOT
# ======================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(cb))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

print("💎 GLASS BOT RUNNING 24/7")
app.run_polling()
