import json
import os

LOCALES_DIR = "locales"

def load_locales():
    locales = {}
    if not os.path.exists(LOCALES_DIR):
        os.makedirs(LOCALES_DIR)
    for file in os.listdir(LOCALES_DIR):
        if file.endswith(".json") and file != "template.json":
            lang_code = file.replace(".json", "")
            with open(os.path.join(LOCALES_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                locales[lang_code] = data
    return locales

def get_localized_string(locales_dict, lang, key, **kwargs):
    """Возвращает локализованную строку с подстановкой аргументов."""
    value = locales_dict.get(lang, {}).get(key, key)
    if kwargs:
        try:
            return value.format(**kwargs)
        except:
            return value
    return value

def get_lang_display(locales_dict):
    """Возвращает словарь {ключ_языка: отображаемый_код} из поля lang_code."""
    return {lang: data.get('lang_code', lang.upper()) for lang, data in locales_dict.items()}