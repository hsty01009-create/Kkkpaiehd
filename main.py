import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command

from config import BOT_TOKEN
from database import *
from keyboards import *
from languages import TEXT
from image import edit_image, make_sticker

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# START + دعوت
@dp.message(Command("start"))
async def start(m: Message):
    args = m.text.split()

    inviter = 0
    if len(args) > 1:
        try:
            inviter = int(args[1])
        except:
            inviter = 0

    await add_user(m.from_user.id, inviter)

    # 👥 پاداش دعوت واقعی
    if inviter != 0:
        await reward_invite(inviter)

    user = await get_user(m.from_user.id)

    if user[3] == 0:
        await m.answer("📜 قوانین را قبول کن", reply_markup=rules())
    else:
        await m.answer("🌍 انتخاب زبان", reply_markup=lang())


# قوانین
@dp.callback_query(F.data == "accept")
async def accept_rules(c: CallbackQuery):
    await accept(c.from_user.id)
    await c.message.answer("🌍 انتخاب زبان", reply_markup=lang())
    await c.message.delete()


# زبان
@dp.callback_query(F.data.in_(["fa","en","ru","es","hi","tr","fr"]))
async def set_lang(c: CallbackQuery):
    await set_lang(c.from_user.id, c.data)
    await c.message.delete()
    await c.message.answer(TEXT[c.data], reply_markup=menu())


# سکه
@dp.callback_query(F.data == "coins")
async def coins(c: CallbackQuery):
    user = await get_user(c.from_user.id)
    await c.message.answer(f"💰 {user[1]}")


# دعوت لینک
@dp.callback_query(F.data == "invite")
async def invite(c: CallbackQuery):
    link = f"https://t.me/{(await bot.get_me()).username}?start={c.from_user.id}"
    await c.message.answer(f"👥 لینک دعوت شما:\n{link}\n\n💰 +200 سکه برای هر دعوت!")


# ادیت عکس
@dp.message(F.photo)
async def photo(m: Message):
    file = await m.bot.get_file(m.photo[-1].file_id)
    await m.bot.download_file(file.file_path, "in.jpg")

    out = edit_image("in.jpg")
    await m.answer_photo(FSInputFile(out))


# استیکر
@dp.message(F.photo)
async def sticker(m: Message):
    file = await m.bot.get_file(m.photo[-1].file_id)
    await m.bot.download_file(file.file_path, "in2.jpg")

    out = make_sticker("in2.jpg")
    await m.answer_sticker(FSInputFile(out))


# RUN
async def main():
    await init()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
