import aiosqlite
import datetime

DB = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 100,
            lang TEXT DEFAULT 'fa',
            accepted INTEGER DEFAULT 0,
            last_daily TEXT DEFAULT ''
        )
        """)
        await db.commit()


async def add_user(user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return await cur.fetchone()


async def set_lang(user_id, lang):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
        await db.commit()


async def accept(user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET accepted=1 WHERE user_id=?", (user_id,))
        await db.commit()


async def add_coins(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def daily(user_id):
    today = str(datetime.date.today())
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET last_daily=? WHERE user_id=?", (today, user_id))
        await db.commit()
