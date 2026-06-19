import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 100,
    lang TEXT DEFAULT 'fa',
    invited_by INTEGER
)
""")

conn.commit()

def get_user(user_id):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cur.fetchone()

def add_user(user_id, invited_by=None):
    if not get_user(user_id):
        cur.execute("INSERT INTO users (user_id, invited_by) VALUES (?,?)", (user_id, invited_by))
        conn.commit()

def set_lang(user_id, lang):
    cur.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
    conn.commit()

def get_coins(user_id):
    cur.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    return cur.fetchone()[0]
