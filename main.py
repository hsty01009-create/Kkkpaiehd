import os
import sqlite3

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# فایل‌های پروژه
from database import (
    add_user,
    get_user,
    get_coins,
    add_coins,
    set_lang,
    get_lang
)

from texts import (
    LANGS,
    welcome
)

from rules import RULES

from image_tools import (
    generate_image_url
)

from sticker import (
    create_sticker
)

# ==========================
# تنظیمات ربات
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

CREATOR = "امیر علی فروزان اصل"

# وضعیت کاربران
user_states = {}

# حالت‌ها
WAITING_IMAGE_PROMPT = "waiting_image_prompt"
WAITING_STICKER_PHOTO = "waiting_sticker_photo"
WAITING_EDIT_PHOTO = "waiting_edit_photo"

# ==========================
# بررسی توکن
# ==========================

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN not found in Railway Variables"
    )

# ==========================
# منوی اصلی
# ==========================

def main_menu(lang="fa"):

    if lang == "fa":
        keyboard = [
            [
                InlineKeyboardButton(
                    "🌍 زبان",
                    callback_data="language"
                ),
                InlineKeyboardButton(
                    "💰 سکه",
                    callback_data="coins"
                )
            ],
            [
                InlineKeyboardButton(
                    "👥 دعوت دوستان",
                    callback_data="invite"
                ),
                InlineKeyboardButton(
                    "📜 قوانین",
                    callback_data="rules"
                )
            ],
            [
                InlineKeyboardButton(
                    "🖼 ساخت عکس",
                    callback_data="image_ai"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎭 ساخت استیکر",
                    callback_data="sticker"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎨 ادیت عکس",
                    callback_data="edit_photo"
                )
            ]
        ]

    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🌍 Language",
                    callback_data="language"
                ),
                InlineKeyboardButton(
                    "💰 Coins",
                    callback_data="coins"
                )
            ],
            [
                InlineKeyboardButton(
                    "👥 Invite",
                    callback_data="invite"
                ),
                InlineKeyboardButton(
                    "📜 Rules",
                    callback_data="rules"
                )
            ],
            [
                InlineKeyboardButton(
                    "🖼 AI Image",
                    callback_data="image_ai"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎭 Sticker",
                    callback_data="sticker"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎨 Edit Photo",
                    callback_data="edit_photo"
                )
            ]
        ]

    return InlineKeyboardMarkup(keyboard)
    # ==========================
# START
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    invited_by = None

    if context.args:
        try:
            invited_by = int(context.args[0])
        except:
            pass

    add_user(user.id, invited_by)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ قبول قوانین",
                callback_data="accept_rules"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ رد قوانین",
                callback_data="reject_rules"
            )
        ]
    ])

    await update.message.reply_text(
        RULES,
        reply_markup=keyboard
    )


# ==========================
# CALLBACKS
# ==========================

async def buttons(update: Update,
                  context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    data = query.data

    # حذف دکمه‌ها بعد از کلیک
    try:
        await query.edit_message_reply_markup(
            reply_markup=None
        )
    except:
        pass

    # ======================
    # قبول قوانین
    # ======================

    if data == "accept_rules":

        keyboard = []

        row = []

        for code, name in LANGS.items():

            row.append(
                InlineKeyboardButton(
                    name,
                    callback_data=f"lang_{code}"
                )
            )

            if len(row) == 2:
                keyboard.append(row)
                row = []

        if row:
            keyboard.append(row)

        await query.message.reply_text(
            "🌍 زبان خود را انتخاب کنید",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    # ======================
    # رد قوانین
    # ======================

    elif data == "reject_rules":

        await query.message.reply_text(
            "❌ تا زمانی که قوانین را قبول نکنید امکان استفاده از ربات را ندارید."
        )

    # ======================
    # انتخاب زبان
    # ======================

    elif data.startswith("lang_"):

        lang = data.replace("lang_", "")

        set_lang(user_id, lang)

        coins = get_coins(user_id)

        await query.message.reply_text(
            welcome(lang, coins),
            reply_markup=main_menu(lang)
        )

    # ======================
    # قوانین
    # ======================

    elif data == "rules":

        await query.message.reply_text(
            RULES
        )

    # ======================
    # سکه
    # ======================

    elif data == "coins":

        coins = get_coins(user_id)

        await query.message.reply_text(
            f"💰 Coins: {coins}"
        )

    # ======================
    # دعوت دوستان
    # ======================

    elif data == "invite":

        bot_username = (
            await context.bot.get_me()
        ).username

        link = (
            f"https://t.me/{bot_username}"
            f"?start={user_id}"
        )

        await query.message.reply_text(
            f"""
👥 لینک دعوت شما:

{link}

🎁 پاداش:
+200 سکه برای هر دعوت موفق
"""
               )
        # ==========================
# ساخت عکس AI
# ==========================

    elif data == "image_ai":

        user_states[user_id] = WAITING_IMAGE_PROMPT

        await query.message.reply_text(
            "🖼 متن عکس را ارسال کنید"
        )

    # ==========================
    # استیکرساز
    # ==========================

    elif data == "sticker":

        user_states[user_id] = WAITING_STICKER_PHOTO

        await query.message.reply_text(
            "🎭 عکس را ارسال کنید"
        )

    # ==========================
    # ادیت عکس
    # ==========================

    elif data == "edit_photo":

        user_states[user_id] = WAITING_EDIT_PHOTO

        await query.message.reply_text(
            "🎨 عکس را ارسال کنید"
        )


# ==========================
# دریافت متن
# ==========================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    state = user_states.get(user_id)

    # ساخت عکس
    if state == WAITING_IMAGE_PROMPT:

        prompt = update.message.text

        url = generate_image_url(prompt)

        await update.message.reply_photo(
            photo=url,
            caption="✅ تصویر ساخته شد"
        )

        user_states.pop(user_id, None)

        return


# ==========================
# دریافت عکس
# ==========================

async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    state = user_states.get(user_id)

    photo = update.message.photo[-1]

    file = await photo.get_file()

    # ----------------------
    # استیکرساز
    # ----------------------

    if state == WAITING_STICKER_PHOTO:

        await file.download_to_drive(
            "user_photo.jpg"
        )

        sticker_file = create_sticker(
            "user_photo.jpg"
        )

        with open(sticker_file, "rb") as s:

            await update.message.reply_sticker(
                sticker=s
            )

        user_states.pop(user_id, None)

        return

    # ----------------------
    # ادیت عکس ساده
    # ----------------------

    elif state == WAITING_EDIT_PHOTO:

        await file.download_to_drive(
            "edit_photo.jpg"
        )

        from PIL import Image, ImageFilter

        img = Image.open(
            "edit_photo.jpg"
        )

        img = img.filter(
            ImageFilter.SHARPEN
        )

        img.save(
            "edited_photo.jpg"
        )

        await update.message.reply_photo(
            photo=open(
                "edited_photo.jpg",
                "rb"
            ),
            caption="✅ عکس ویرایش شد"
        )

        user_states.pop(user_id, None)

        return


# ==========================
# MAIN
# ==========================

def main():

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            buttons
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT &
            ~filters.COMMAND,
            text_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            photo_handler
        )
    )

    print("Bot Started")

    app.run_polling()


if __name__ == "__main__":
    main()
