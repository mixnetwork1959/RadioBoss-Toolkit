from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


APP_DIRECTORY = "RadioBOSS Library Cleaner"
SETTINGS_FILENAME = "settings.json"


def settings_path() -> Path:
    root = os.environ.get("LOCALAPPDATA")
    if root:
        return Path(root) / APP_DIRECTORY / SETTINGS_FILENAME
    return Path.home() / APP_DIRECTORY / SETTINGS_FILENAME


def load_settings(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else settings_path()
    try:
        data = json.loads(target.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(values: dict[str, Any], path: str | Path | None = None) -> bool:
    target = Path(path) if path is not None else settings_path()
    temporary = target.with_suffix(target.suffix + ".tmp")
    payload = {"sqlite_path": str(values.get("sqlite_path", ""))}
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(target)
        return True
    except (OSError, TypeError, ValueError):
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        return False
