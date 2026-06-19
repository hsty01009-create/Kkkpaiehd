LANGS = {
    "fa": "فارسی",
    "en": "English",
    "ar": "Arabic",
    "tr": "Türkçe",
    "de": "Deutsch",
    "ru": "Русский",
    "fr": "Français"
}

def welcome(lang, coins):
    if lang == "fa":
        return f"سلام 👋\n💰 سکه: {coins}"
    if lang == "en":
        return f"Hello 👋\n💰 Coins: {coins}"
    return f"Welcome 👋\nCoins: {coins}"
