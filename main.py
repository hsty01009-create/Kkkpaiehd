import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command

from config import BOT_TOKEN
from database import *
from keyboards import menu, rules, lang
from image import make_image, edit_image

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# START + دعوت
@dp.message(Command("start"))
async def start(message: Message):
    args = message.text.split()

    invite_by = 0
    if len(args) > 1:
        try:
            invite_by = int(args[1])
        except:
            pass

    await add_user(message.from_user.id, invite_by)

    user = await get_user(message.from_user.id)

    if user[3] == 0:
        await message.answer("📜 قوانین را قبول کن", reply_markup=rules())
    else:
        await message.answer("🌍 انتخاب زبان", reply_markup=lang())


# قبول قوانین
@dp.callback_query(F.data == "accept")
async def accept_rules(call: CallbackQuery):
    await accept(call.from_user.id)
    await call.message.answer("🌍 انتخاب زبان", reply_markup=lang())


# زبان
@dp.callback_query(F.data.in_(["fa","en","ru","es","hi","tr","fr"]))
async def set_language(call: CallbackQuery):
    await set_lang(call.from_user.id, call.data)
    await call.message.answer("✨ خوش آمدی", reply_markup=menu())


# ساخت عکس
@dp.callback_query(F.data == "img")
async def img(call: CallbackQuery):
    path = make_image("سلام 👋")
    await call.message.answer_photo(FSInputFile(path))


# ادیت عکس
@dp.callback_query(F.data == "edit")
async def edit(call: CallbackQuery):
    await call.message.answer("📸 عکس بفرست")


@dp.message(F.photo)
async def photo(message: Message):
    file = await message.bot.get_file(message.photo[-1].file_id)
    await message.bot.download_file(file.file_path, "in.jpg")

    out = edit_image("in.jpg")
    await message.answer_photo(FSInputFile(out))


# سکه
@dp.callback_query(F.data == "coins")
async def coins(call: CallbackQuery):
    user = await get_user(call.from_user.id)
    await call.message.answer(f"💰 {user[1]}")


# روزانه
@dp.callback_query(F.data == "daily")
async def daily(call: CallbackQuery):
    await add_coins(call.from_user.id, 100)
    await call.message.answer("🎁 +100 سکه")


# دعوت دوستان (200 سکه آماده توسعه)
@dp.callback_query(F.data == "invite")
async def invite(call: CallbackQuery):
    await add_coins(call.from_user.id, 200)
    await call.message.answer("👥 +200 سکه (دعوت فعال شد)")


async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
