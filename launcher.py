"""RadioBOSS Toolkit Launcher."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from toolkit_common import LANGUAGES, load_toolkit_settings, save_language, toolkit_root, tr


VERSION = "0.3.2"


def application_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


ROOT_DIR = application_dir()
TOOLS_DIR = ROOT_DIR / "tools"
AUDIO_DIR = TOOLS_DIR / "Audio Toolkit"
SCAN_REPORT = AUDIO_DIR / "silence_report.csv"

PROGRAMS = {
    "scheduler": TOOLS_DIR / "Broadcast Scheduler" / "BroadcastScheduler.exe",
    "cleaner": TOOLS_DIR / "Library Cleaner" / "RadioBOSS-Library-Cleaner.exe",
    "scanner": AUDIO_DIR / "SilenceScanner.exe",
    "cutter": AUDIO_DIR / "AutoCutter.exe",
    "songsync": TOOLS_DIR / "SongSync" / "RadioBOSS-SongSync.exe",
    "songsync_setup": TOOLS_DIR / "SongSync" / "RadioBOSS-SongSync-Setup.exe",
}


def resolve_program(key: str) -> Path:
    """Find a tool even if its EXE was moved inside the toolkit folder."""
    expected = PROGRAMS[key]
    if expected.is_file():
        return expected
    matches = list(toolkit_root().rglob(expected.name))
    return matches[0] if matches else expected


def launch_program(key: str) -> None:
    executable = resolve_program(key)
    if not executable.is_file():
        messagebox.showerror("Program not found", f"The program could not be found:\n\n{executable}\n\nPlease keep the complete RadioBOSS Toolkit folder together.")
        return
    if key == "cutter" and not confirm_cutter():
        return
    try:
        creation_flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
        subprocess.Popen([str(executable)], cwd=str(executable.parent), creationflags=creation_flags)
    except OSError as error:
        messagebox.showerror("Unable to start program", str(error))


def confirm_cutter() -> bool:
    lang = load_toolkit_settings()["language"]
    if not SCAN_REPORT.is_file():
        messagebox.showwarning(tr(lang, "scan_required"), tr(lang, "scan_missing"))
        return False
    modified = datetime.fromtimestamp(SCAN_REPORT.stat().st_mtime)
    timestamp = modified.strftime("%Y-%m-%d %H:%M")
    return messagebox.askyesno(tr(lang, "cutter_title"), tr(lang, "cutter_confirm").format(timestamp=timestamp), icon="warning")


class ToolkitApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"RadioBOSS Toolkit v{VERSION}")
        self.geometry("760x680")
        self.minsize(680, 600)
        self.configure(bg="#eef2f7")
        self.language = load_toolkit_settings()["language"]
        self.language_var = tk.StringVar(value=self.language)
        self._set_icon(); self._build_styles(); self._build_menu(); self._build_ui()

    def _build_menu(self) -> None:
        menu = tk.Menu(self); settings_menu = tk.Menu(menu, tearoff=False); language_menu = tk.Menu(settings_menu, tearoff=False)
        for code, label in LANGUAGES.items():
            language_menu.add_radiobutton(label=label, value=code, variable=self.language_var, command=lambda value=code: self._set_language(value))
        settings_menu.add_cascade(label=tr(self.language, "language"), menu=language_menu); menu.add_cascade(label=tr(self.language, "settings"), menu=settings_menu)
        help_menu = tk.Menu(menu, tearoff=False); help_menu.add_command(label=tr(self.language, "user_guide"), command=self._open_guide); help_menu.add_command(label=tr(self.language, "open_folder"), command=self._open_folder); help_menu.add_separator(); help_menu.add_command(label=tr(self.language, "about"), command=self._about); menu.add_cascade(label=tr(self.language, "help"), menu=help_menu); self.configure(menu=menu)

    def _set_language(self, language: str) -> None:
        self.language = language; self.language_var.set(language); save_language(language)
        for child in self.winfo_children(): child.destroy()
        self._build_menu(); self._build_ui()

    def _open_guide(self) -> None:
        filename = f"index_{self.language}.html"
        for guide in (toolkit_root() / "help" / filename, resource_dir() / "help" / filename):
            if guide.is_file(): os.startfile(guide); return
        messagebox.showwarning(tr(self.language, "help"), tr(self.language, "guide_missing"))

    def _open_folder(self) -> None: os.startfile(toolkit_root())

    def _about(self) -> None:
        messagebox.showinfo(tr(self.language, "about"), f"RadioBOSS Toolkit\nVersion {VERSION}\nBuild: 2026-08-22\n\nBroadcast Scheduler 4.5.1\nLibrary Cleaner 1.0.1\nSilence Scanner GUI 1.0.0\nAuto Cutter GUI 1.0.0\nSongSync Engine 1.7.2\n\nCreated by Raymond Ummels\nDeveloped with assistance from OpenAI ChatGPT\n\n© 2026 Raymond Ummels\nMIT License")

    def _set_icon(self) -> None:
        try: self.iconbitmap(default=str(resource_dir() / "assets" / "radioboss-toolkit.ico"))
        except tk.TclError: pass

    def _build_styles(self) -> None:
        style = ttk.Style(self); style.theme_use("clam"); style.configure("App.TFrame", background="#eef2f7"); style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground="#07153d", background="#eef2f7"); style.configure("Sub.TLabel", font=("Segoe UI", 11), foreground="#526176", background="#eef2f7"); style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1); style.configure("CardTitle.TLabel", font=("Segoe UI", 14, "bold"), foreground="#07153d", background="white"); style.configure("CardText.TLabel", font=("Segoe UI", 9), foreground="#526176", background="white"); style.configure("Tool.TButton", font=("Segoe UI", 10, "bold"), padding=(18, 9)); style.map("Tool.TButton", background=[("active", "#ffb563"), ("!disabled", "#ff9f43")], foreground=[("!disabled", "#07153d")])

    def _build_ui(self) -> None:
        header = ttk.Frame(self, style="App.TFrame"); header.pack(fill="x", padx=34, pady=(28, 18)); ttk.Label(header, text="RadioBOSS Toolkit", style="Title.TLabel").pack(anchor="w"); ttk.Label(header, text=tr(self.language, "tagline"), style="Sub.TLabel").pack(anchor="w", pady=(2, 0))
        grid = ttk.Frame(self, style="App.TFrame"); grid.pack(fill="both", expand=True, padx=28, pady=4); grid.columnconfigure((0, 1), weight=1, uniform="cards"); grid.rowconfigure((0, 1, 2), weight=1, uniform="cards")
        cards = [(tr(self.language, "scheduler"), tr(self.language, "scheduler_desc"), "scheduler"), (tr(self.language, "cleaner"), tr(self.language, "cleaner_desc"), "cleaner"), (tr(self.language, "scanner"), tr(self.language, "scanner_desc"), "scanner"), (tr(self.language, "cutter"), tr(self.language, "cutter_desc"), "cutter"), (tr(self.language, "songsync"), tr(self.language, "songsync_desc"), "songsync")]
        for index, (title, description, key) in enumerate(cards): self._card(grid, index // 2, index % 2, title, description, key)
        ttk.Label(self, text=f"Version {VERSION}  •  {tr(self.language, 'portable')}", style="Sub.TLabel").pack(pady=(12, 18))

    def _card(self, parent, row, column, title, description, key) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=20); card.grid(row=row, column=column, sticky="nsew", padx=7, pady=7); ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w"); ttk.Label(card, text=description, style="CardText.TLabel", wraplength=270, justify="left").pack(anchor="w", pady=(8, 18))
        if key == "songsync":
            buttons = ttk.Frame(card, style="Card.TFrame"); buttons.pack(anchor="w", side="bottom"); ttk.Button(buttons, text=tr(self.language, "sync_now"), style="Tool.TButton", command=lambda: launch_program("songsync")).pack(side="left"); ttk.Button(buttons, text=tr(self.language, "setup"), style="Tool.TButton", command=lambda: launch_program("songsync_setup")).pack(side="left", padx=(8, 0))
        else: ttk.Button(card, text=tr(self.language, "open"), style="Tool.TButton", command=lambda: launch_program(key)).pack(anchor="w", side="bottom")


if __name__ == "__main__": ToolkitApp().mainloop()
