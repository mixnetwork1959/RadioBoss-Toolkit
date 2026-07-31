# ==========================================
# Broadcast Scheduler
# Version 4.5.0
# config.py
# ==========================================

import json
import os
from pathlib import Path

SETTINGS_FILE = "settings.json"


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "admin_sdl": "",
            "theme": "radio_albena",
            "export_directory": ""
        }

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        settings = json.load(f)

    settings.setdefault("theme", "radio_albena")
    settings.setdefault("export_directory", "")

    return settings


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


def get_default_export_directory():
    """Return a visible, user-facing folder for website exports."""

    documents = None

    if os.name == "nt":
        try:
            import ctypes

            buffer = ctypes.create_unicode_buffer(260)
            result = ctypes.windll.shell32.SHGetFolderPathW(
                None,
                5,  # CSIDL_PERSONAL (Documents)
                None,
                0,
                buffer
            )

            if result == 0 and buffer.value:
                documents = Path(buffer.value)

        except (AttributeError, OSError):
            documents = None

    if documents is None:
        documents = Path.home() / "Documents"

    return documents / "Broadcast Scheduler" / "Export"
