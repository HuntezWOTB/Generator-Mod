import os
import json
import platform
import tkinter as tk

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "language": "en",
    "theme": "system",
    "mode": "DVPL",          # теперь по умолчанию DVPL
    "game_path": "",
    "use_dlc": False
}

def get_system_language():
    import locale
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith("ru"):
            return "ru"
    except:
        pass
    return "en"

def get_system_theme():
    import subprocess
    try:
        result = subprocess.run(
            ['reg', 'query', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize', '/v', 'AppsUseLightTheme'],
            capture_output=True, text=True
        )
        if "0x0" in result.stdout:
            return "dark"
    except:
        pass
    return "light"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        cfg = DEFAULT_CONFIG.copy()
        cfg["language"] = get_system_language()
        cfg["theme"] = get_system_theme()
        return cfg

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)