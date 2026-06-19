import sqlite3

conn = sqlite3.connect('bot.db', check_same_thread=False)
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 100,
lang TEXT DEFAULT 'fa'
)''')

conn.commit()

def add_user(user_id):
    cur.execute('INSERT OR IGNORE INTO users(user_id) VALUES(?)',(user_id,))
    conn.commit()

def get_lang(user_id):
    cur.execute('SELECT lang FROM users WHERE user_id=?',(user_id,))
    r = cur.fetchone()
    return r[0] if r else 'fa'

def set_lang(user_id, lang):
    cur.execute('UPDATE users SET lang=? WHERE user_id=?',(lang,user_id))
    conn.commit()
