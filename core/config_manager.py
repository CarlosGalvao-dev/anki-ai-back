# -*- coding: utf-8 -*-
import json
import os

ADDON_PACKAGE = __name__.split(".")[0]

DEFAULT_CONFIG = {
    "api_key": "",
    "model": "gemini-2.0-flash",
    "source_field": "Front",
    "target_field": "Back",
    "append": False,
    "shortcut": "Ctrl+Shift+G",
    "system_prompt": ""
}

def _get_local_config_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "config.json")

def load_config() -> dict:
    """Carrega a configuração via Anki addonManager ou fallback para config.json local."""
    config = dict(DEFAULT_CONFIG)
    
    # Tenta carregar do Anki
    try:
        from aqt import mw
        if mw and mw.addonManager:
            addon_config = mw.addonManager.getConfig(ADDON_PACKAGE)
            if addon_config:
                config.update(addon_config)
                return config
    except ImportError:
        pass

    # Fallback para config.json
    local_path = _get_local_config_path()
    if os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config.update(saved)
        except Exception:
            pass

    return config

def save_config(new_config: dict) -> bool:
    """Salva as configurações via Anki addonManager ou diretamente no config.json."""
    # Tenta salvar pelo Anki
    try:
        from aqt import mw
        if mw and mw.addonManager:
            mw.addonManager.writeConfig(ADDON_PACKAGE, new_config)
            return True
    except ImportError:
        pass

    # Fallback para escrita em arquivo
    local_path = _get_local_config_path()
    try:
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False
