LANGS = {
    "fa": "فارسی",
    "en": "English",
    "ar": "العربية",
    "ru": "Русский",
    "tr": "Türkçe",
    "de": "Deutsch",
    "fr": "Français"
}

def welcome(lang, coins):
    if lang == "fa":
        return f"👋 خوش آمدی!\n💰 سکه: {coins}"
    return f"Welcome!\nCoins: {coins}"
