import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command

from config import BOT_TOKEN, CREATOR
from database import *
from keyboards import *
from messages import RULES, welcome
from image import edit_image, make_sticker

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

user_state = {}


# START
@dp.message(Command("start"))
async def start(m: Message):
    await add_user(m.from_user.id)

    user = await get_user(m.from_user.id)

    if user[3] == 0:
        await m.answer(RULES, reply_markup=rules())
    else:
        await m.answer("🌍 انتخاب زبان", reply_markup=lang())


# ACCEPT RULES
@dp.callback_query(F.data == "accept")
async def accept_rules(c: CallbackQuery):
    await accept(c.from_user.id)
    await c.message.delete()
    await c.message.answer("🌍 زبان را انتخاب کن", reply_markup=lang())


# LANGUAGE
@dp.callback_query(F.data.in_(["fa","en","ru","es","hi","tr","fr"]))
async def set_language(c: CallbackQuery):
    await set_lang(c.from_user.id, c.data)

    user = await get_user(c.from_user.id)

    await c.message.delete()

    await c.message.answer(
        welcome(c.data, user[1], CREATOR),
        reply_markup=menu()
    )


# COINS
@dp.callback_query(F.data == "coins")
async def coins(c: CallbackQuery):
    user = await get_user(c.from_user.id)
    await c.message.answer(f"💰 {user[1]}")


# INVITE
@dp.callback_query(F.data == "invite")
async def invite(c: CallbackQuery):
    link = f"https://t.me/{(await bot.get_me()).username}?start={c.from_user.id}"
    await c.message.answer(f"👥 لینک دعوت:\n{link}\n💰 +200 سکه")


# EDIT MODE
@dp.callback_query(F.data == "edit")
async def edit_mode(c: CallbackQuery):
    user_state[c.from_user.id] = "edit"
    await c.message.answer("📸 عکس بفرست برای ادیت")


# STICKER MODE
@dp.callback_query(F.data == "sticker")
async def sticker_mode(c: CallbackQuery):
    user_state[c.from_user.id] = "sticker"
    await c.message.answer("📸 عکس بفرست برای استیکر")


# SINGLE PHOTO HANDLER (FIXED)
@dp.message(F.photo)
async def photo_handler(m: Message):
    state = user_state.get(m.from_user.id)

    file = await m.bot.get_file(m.photo[-1].file_id)
    await m.bot.download_file(file.file_path, "in.jpg")

    if state == "edit":
        out = edit_image("in.jpg")
        await m.answer_photo(FSInputFile(out))

    elif state == "sticker":
        out = make_sticker("in.jpg")
        await m.answer_sticker(FSInputFile(out))

    else:
        await m.answer("❌ اول از منو انتخاب کن")

    user_state[m.from_user.id] = None


# RUN
async def main():
    await init()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
