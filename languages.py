texts = {
    "fa": {"welcome": "✨ خوش آمدی", "coins": "💰 سکه تو: "},
    "en": {"welcome": "✨ Welcome", "coins": "Coins: "},
    "ru": {"welcome": "✨ Добро пожаловать", "coins": "Монеты: "},
    "es": {"welcome": "✨ Bienvenido", "coins": "Monedas: "},
    "hi": {"welcome": "✨ स्वागत है", "coins": "सिक्के: "},
    "tr": {"welcome": "✨ Hoş geldin", "coins": "Jeton: "},
    "fr": {"welcome": "✨ Bienvenue", "coins": "Pièces: "}
}

def t(lang, key):
    return texts.get(lang, texts["fa"]).get(key, key)
