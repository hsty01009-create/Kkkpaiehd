LANGS = {
    "fa": "🇮🇷 فارسی",
    "en": "🇺🇸 English",
    "ar": "🇸🇦 عربي",
    "tr": "🇹🇷 Türkçe",
    "ru": "🇷🇺 Русский",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français"
}


def welcome(lang, coins):
    return {
        "fa": f"👋 خوش آمدی!\n💰 سکه: {coins}",
        "en": f"Welcome!\nCoins: {coins}",
        "ar": f"مرحبا!\nCoins: {coins}",
        "tr": f"Hoş geldin!\nCoins: {coins}",
        "ru": f"Добро пожаловать!\nCoins: {coins}",
        "de": f"Willkommen!\nCoins: {coins}",
        "fr": f"Bienvenue!\nCoins: {coins}",
    }.get(lang, "Welcome!")
