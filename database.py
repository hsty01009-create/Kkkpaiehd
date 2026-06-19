import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    lang TEXT DEFAULT 'fa',
    invited_by INTEGER
)
""")

conn.commit()


def add_user(user_id, invited_by=None):
    cur.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (id, coins, invited_by) VALUES (?, ?, ?)",
                    (user_id, 0, invited_by))
        conn.commit()


def get_user(user_id):
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    return cur.fetchone()


def add_coins(user_id, amount):
    cur.execute("UPDATE users SET coins = coins + ? WHERE id=?", (amount, user_id))
    conn.commit()


def set_lang(user_id, lang):
    cur.execute("UPDATE users SET lang=? WHERE id=?", (lang, user_id))
    conn.commit()


def get_lang(user_id):
    cur.execute("SELECT lang FROM users WHERE id=?", (user_id,))
    r = cur.fetchone()
    return r[0] if r else "fa"
