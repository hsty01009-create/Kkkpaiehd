import asyncio
import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command

from config import BOT_TOKEN, CREATOR
from database import *
from keyboards import menu, rules_kb, lang_kb
from image import make_image, make_sticker
from languages import t

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# START
@dp.message(Command("start"))
async def start(message: Message):
    ref = message.text.split()
    ref_by = int(ref[1]) if len(ref) > 1 else 0

    await add_user(message.from_user.id, ref_by)

    user = await get_user(message.from_user.id)

    if user[3] == 0:
        await message.answer("📜 قوانین را قبول کن", reply_markup=rules_kb())
    else:
        await message.answer("🌍 زبان را انتخاب کن", reply_markup=lang_kb())


# RULES
@dp.callback_query(F.data == "accept")
async def accept(call: CallbackQuery):
    await accept_rules(call.from_user.id)
    await call.message.answer("🌍 حالا زبان را انتخاب کن", reply_markup=lang_kb())


@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.split("_")[1]
    await set_lang(call.from_user.id, lang)

    user = await get_user(call.from_user.id)

    await call.message.answer(f"""
✨ {t(lang,'welcome')}

💰 سکه تو: {user[1]}
🌍 زبان: {lang}

━━━━━━━━━━━━
👨‍💻 سازنده: {CREATOR}
""", reply_markup=menu())


# COINS
@dp.callback_query(F.data == "coins")
async def coins(call: CallbackQuery):
    user = await get_user(call.from_user.id)
    await call.message.answer(f"💰 {user[1]}")


# DAILY
@dp.callback_query(F.data == "daily")
async def daily(call: CallbackQuery):
    user = await get_user(call.from_user.id)
    today = str(datetime.date.today())

    if user[4] == today:
        await call.message.answer("⛔ امروز گرفتی")
    else:
        await add_coins(call.from_user.id, 100)
        await set_daily(call.from_user.id)
        await call.message.answer("🎁 +100 سکه")


# IMAGE
@dp.callback_query(F.data == "image")
async def image(call: CallbackQuery):
    path = make_image("سلام 👋")
    await call.message.answer_photo(FSInputFile(path))


# STICKER
@dp.callback_query(F.data == "sticker")
async def sticker(call: CallbackQuery):
    await call.message.answer("📸 عکس بفرست")


@dp.message(F.photo)
async def handle_photo(message: Message):
    file = await message.bot.get_file(message.photo[-1].file_id)
    await message.bot.download_file(file.file_path, "in.jpg")

    out = make_sticker("in.jpg")

    await message.answer_sticker(FSInputFile(out))


# RUN
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
