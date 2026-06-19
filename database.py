import aiosqlite

DB_NAME = "users.db"

async def init_db():
async with aiosqlite.connect(DB_NAME) as db:
await db.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
username TEXT,
first_name TEXT,
language TEXT DEFAULT 'fa',
credits INTEGER DEFAULT 10,
accepted_rules INTEGER DEFAULT 0,
inviter INTEGER DEFAULT 0
)
""")
await db.commit()

async def add_user(user_id, username, first_name):
async with aiosqlite.connect(DB_NAME) as db:
await db.execute(
"INSERT OR IGNORE INTO users(user_id,username,first_name) VALUES(?,?,?)",
(user_id, username, first_name)
)
await db.commit()

async def get_user(user_id):
async with aiosqlite.connect(DB_NAME) as db:
cur = await db.execute(
"SELECT * FROM users WHERE user_id=?",
(user_id,)
)
return await cur.fetchone()
