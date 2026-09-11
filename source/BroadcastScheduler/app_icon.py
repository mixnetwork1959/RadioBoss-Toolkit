"""Windows application icon helpers for RadioBOSS Broadcast Scheduler."""

from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

APP_USER_MODEL_ID = "RadioBOSS.BroadcastScheduler.4.5.1"
ICON_NAME = "radioboss-toolkit.ico"


def set_windows_app_id() -> None:
    """Give Windows a stable identity so the taskbar uses the app icon."""
    if os.name != "nt":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except Exception:
        pass


def _icon_candidates() -> list[Path]:
    candidates: list[Path] = []

    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        candidates.append(Path(bundle_root) / "assets" / ICON_NAME)

    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "assets" / ICON_NAME)

    source_file = Path(__file__).resolve()
    candidates.append(source_file.parents[2] / "assets" / ICON_NAME)
    candidates.append(Path.cwd() / "assets" / ICON_NAME)

    return candidates


def apply_window_icon(window) -> None:
    """Apply the bundled ICO to a Tk/Toplevel window when available."""
    for icon_path in _icon_candidates():
        if not icon_path.is_file():
            continue
        try:
            window.iconbitmap(default=str(icon_path))
            return
        except Exception:
            continue
