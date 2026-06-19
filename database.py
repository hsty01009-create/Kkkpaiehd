import aiosqlite

DB = "bot.db"

async def init():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 100,
            lang TEXT DEFAULT 'fa',
            invited_by INTEGER DEFAULT 0
        )
        """)
        await db.commit()

async def add_user(uid):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (uid,))
        await db.commit()

async def get_user(uid):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        return await cur.fetchone()

async def update_lang(uid, lang):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, uid))
        await db.commit()

async def add_coins(uid, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, uid))
        await db.commit()
