import locale
import json
from pathlib import Path

# Load dynamic translation databases from local JSON files
STRINGS = {}
LOCALES_DIR = Path(__file__).parent / "locales"

# Auto-detect system language
ACTIVE_LANG = "en"
try:
    system_locale = locale.getdefaultlocale()[0]
    if system_locale and system_locale.startswith("es"):
        ACTIVE_LANG = "es"
except Exception:
    pass

def load_locale(lang):
    """Loads a specific locale JSON into the STRINGS cache."""
    if lang in STRINGS:
        return STRINGS[lang]
    
    locale_file = LOCALES_DIR / f"{lang}.json"
    if locale_file.exists():
        try:
            with open(locale_file, "r", encoding="utf-8") as f:
                STRINGS[lang] = json.load(f)
                return STRINGS[lang]
        except Exception as e:
            print(f"[i18n] Error loading locale resource {lang}: {e}")
    return {}

def _(key, **kwargs):
    """Translates the given key into the active system language."""
    # Ensure active and English fallback locales are loaded
    lang_dict = load_locale(ACTIVE_LANG)
    fallback_dict = load_locale("en")
    
    text = lang_dict.get(key, fallback_dict.get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
