import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command

from config import BOT_TOKEN, CREATOR
from rules import RULES
from database import *
from languages import LANG
from image import edit_image, make_sticker

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

state = {}

def welcome(lang, coins, creator):
    return f"""
✨ خوش آمدی

🌍 زبان: {lang}
💰 سکه: {coins}

━━━━━━━━━━━━
👨‍💻 سازنده: {creator}
"""

# START + REF
@dp.message(Command("start"))
async def start(m: Message):
    ref = m.text.split()[1] if len(m.text.split()) > 1 else 0
    await add_user(m.from_user.id, ref)

    await m.answer(RULES)

# LANGUAGE SELECT
@dp.callback_query(F.data.in_(LANG.keys()))
async def lang(c: CallbackQuery):
    await set_lang(c.from_user.id, c.data)
    await first_bonus(c.from_user.id)

    user = await get_user(c.from_user.id)

    if user[3] != 0:
        await reward_invite(user[3])

    await c.message.answer(
        welcome(LANG[c.data], user[1], CREATOR)
    )

# EDIT MODE
@dp.callback_query(F.data == "edit")
async def edit(c: CallbackQuery):
    state[c.from_user.id] = "edit"
    await c.message.answer("📸 عکس بفرست (ادیت 10 سکه)")

# STICKER MODE
@dp.callback_query(F.data == "sticker")
async def sticker(c: CallbackQuery):
    state[c.from_user.id] = "sticker"
    await c.message.answer("📸 عکس بفرست")

# PHOTO HANDLER
@dp.message(F.photo)
async def photo(m: Message):
    file = await bot.get_file(m.photo[-1].file_id)
    await bot.download_file(file.file_path, "in.jpg")

    if state.get(m.from_user.id) == "edit":
        out = edit_image("in.jpg")
        await m.answer_photo(FSInputFile(out))

    elif state.get(m.from_user.id) == "sticker":
        out = make_sticker("in.jpg")
        await m.answer_document(FSInputFile(out))

    state[m.from_user.id] = None

async def main():
    await init()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
