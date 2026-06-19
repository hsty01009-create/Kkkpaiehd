import aiosqlite

DB = "bot.db"

async def init():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 100,
            lang TEXT DEFAULT 'fa',
            accepted INTEGER DEFAULT 0,
            invited_by INTEGER DEFAULT 0
        )
        """)
        await db.commit()

async def add_user(uid, invited_by=0):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users(user_id, invited_by)
        VALUES(?,?)
        """, (uid, invited_by))
        await db.commit()

async def get_user(uid):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        return await cur.fetchone()

async def set_lang(uid, lang):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, uid))
        await db.commit()

async def accept(uid):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET accepted=1 WHERE user_id=?", (uid,))
        await db.commit()

async def add_coins(uid, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET coins=coins+? WHERE user_id=?", (amount, uid))
        await db.commit()


# 👥 سیستم دعوت واقعی
async def reward_invite(inviter_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET coins=coins+200 WHERE user_id=?", (inviter_id,))
        await db.commit()
