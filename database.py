import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 100,
    lang TEXT DEFAULT 'fa',
    invited_by INTEGER
)
""")

conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def add_user(user_id, invited_by=None):
    if not get_user(user_id):
        cursor.execute(
            "INSERT INTO users (user_id, invited_by) VALUES (?,?)",
            (user_id, invited_by)
        )
        conn.commit()

def update_lang(user_id, lang):
    cursor.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
    conn.commit()

def add_coins(user_id, amount):
    cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def get_coins(user_id):
    cursor.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()[0]
