# ==========================================
# Broadcast Scheduler
# Version 4.4.0
# gui_menu.py
# ==========================================

import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from scheduler_i18n import tr
from toolkit_common import LANGUAGES, load_toolkit_settings, save_language, toolkit_root


# =====================================================
# Create Menu
# =====================================================

def create_menu(
    root,
    refresh_command,
    theme_var,
    theme_command,
    themes
):

    menubar = tk.Menu(root)

    file_menu = tk.Menu(
        menubar,
        tearoff=0
    )

    file_menu.add_command(
    label=tr("refresh"),
    command=refresh_command
    )

    file_menu.add_separator()

    file_menu.add_command(
        label=tr("exit"),
        command=root.destroy
    )

    menubar.add_cascade(
        label=tr("file"),
        menu=file_menu
    )

    view_menu = tk.Menu(
        menubar,
        tearoff=0
    )

    theme_menu = tk.Menu(
        view_menu,
        tearoff=0
    )

    for theme_id, theme in themes.items():
        theme_menu.add_radiobutton(
            label=theme["name"],
            value=theme_id,
            variable=theme_var,
            command=theme_command
        )

    view_menu.add_cascade(
        label=tr("theme"),
        menu=theme_menu
    )

    menubar.add_cascade(
        label=tr("view"),
        menu=view_menu
    )

    settings_menu = tk.Menu(menubar, tearoff=0)
    language_menu = tk.Menu(settings_menu, tearoff=0)
    language_var = tk.StringVar(value=load_toolkit_settings()["language"])

    def change_language(code):
        save_language(code)
        command = [sys.executable] if getattr(sys, "frozen", False) else [sys.executable, sys.argv[0]]
        subprocess.Popen(command, cwd=os.getcwd())
        root.destroy()

    for code, label in LANGUAGES.items():
        language_menu.add_radiobutton(label=label, value=code, variable=language_var,
            command=lambda value=code: change_language(value))
    settings_menu.add_cascade(label=tr("language"), menu=language_menu)
    menubar.add_cascade(label=tr("settings"), menu=settings_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    def open_guide():
        guide = toolkit_root() / "help" / f"index_{load_toolkit_settings()['language']}.html"
        if guide.is_file(): os.startfile(guide)
        else: messagebox.showwarning(tr("help"), str(guide))
    help_menu.add_command(label=tr("guide"), command=open_guide)
    help_menu.add_command(label=tr("folder"), command=lambda: os.startfile(toolkit_root()))
    help_menu.add_separator()
    help_menu.add_command(label=tr("about"), command=lambda: messagebox.showinfo(
        tr("about"), "Broadcast Scheduler\nVersion 4.5.1\nBuild: 2026-07-31\n\n"
        f"{tr('created')}\n{tr('assistance')}\n\n© 2026 Raymond Ummels\nMIT License"))
    menubar.add_cascade(label=tr("help"), menu=help_menu)

    root.config(menu=menubar)

    return (
        menubar,
        file_menu,
        view_menu,
        theme_menu
    )
