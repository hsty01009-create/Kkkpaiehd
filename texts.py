LANGS = {
    "fa": "فارسی",
    "en": "English",
    "ar": "العربية",
    "tr": "Türkçe",
    "fr": "Français",
    "es": "Español",
    "ru": "Русский"
}

WELCOME = {
    "fa": """
✨ خوش آمدی به ربات

🌍 زبان: فارسی
💰 سکه: {coins}

━━━━━━━━━━━━
👨‍💻 سازنده: امیر علی فروزان اصل
""",

    "en": """
✨ Welcome

🌍 Language: English
💰 Coins: {coins}

━━━━━━━━━━━━
👨‍💻 Creator: Amir Ali Forouzan Asl
""",

    "ar": """
✨ مرحباً بك

🌍 اللغة: العربية
💰 العملات: {coins}

━━━━━━━━━━━━
👨‍💻 المطور: Amir Ali Forouzan Asl
""",

    "tr": """
✨ Hoş Geldiniz

🌍 Dil: Türkçe
💰 Jeton: {coins}

━━━━━━━━━━━━
👨‍💻 Geliştirici: Amir Ali Forouzan Asl
""",

    "fr": """
✨ Bienvenue

🌍 Langue: Français
💰 Pièces: {coins}

━━━━━━━━━━━━
👨‍💻 Créateur: Amir Ali Forouzan Asl
""",

    "es": """
✨ Bienvenido

🌍 Idioma: Español
💰 Monedas: {coins}

━━━━━━━━━━━━
👨‍💻 Creador: Amir Ali Forouzan Asl
""",

    "ru": """
✨ Добро пожаловать

🌍 Язык: Русский
💰 Монеты: {coins}

━━━━━━━━━━━━
👨‍💻 Создатель: Amir Ali Forouzan Asl
"""
}


def welcome(lang, coins):
    return WELCOME.get(lang, WELCOME["en"]).format(coins=coins)
