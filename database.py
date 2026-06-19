import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    lang TEXT DEFAULT 'fa',
    invited_by INTEGER
)
""")
conn.commit()


def add_user(user_id, invited_by=None):
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (user_id, coins, invited_by) VALUES (?, ?, ?)",
            (user_id, 100, invited_by)   # ⭐ 100 سکه ورود
        )
        conn.commit()


def get_coins(user_id):
    cur.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    r = cur.fetchone()
    return r[0] if r else 0


def add_coins(user_id, amount):
    cur.execute(
        "UPDATE users SET coins = coins + ? WHERE user_id=?",
        (amount, user_id)
    )
    conn.commit()


def set_lang(user_id, lang):
    cur.execute(
        "UPDATE users SET lang=? WHERE user_id=?",
        (lang, user_id)
    )
    conn.commit()


def get_lang(user_id):
    cur.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    r = cur.fetchone()
    return r[0] if r else "fa"


def get_invited_by(user_id):
    cur.execute("SELECT invited_by FROM users WHERE user_id=?", (user_id,))
    r = cur.fetchone()
    return r[0] if r else None
