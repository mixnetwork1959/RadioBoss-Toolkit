# ==========================================
# Broadcast Scheduler
# Version 4.4.0
# theme_manager.py
# ==========================================

from tkinter import ttk


DEFAULT_THEME = "radio_albena"


THEMES = {
    "midnight_studio": {
        "name": "Midnight Studio",
        "background": "#151A22",
        "surface": "#202733",
        "surface_alt": "#293342",
        "input": "#11161D",
        "border": "#3B4656",
        "text": "#F2F5F8",
        "muted": "#B7C0CC",
        "accent": "#4EA3FF",
        "accent_hover": "#72B7FF",
        "accent_text": "#FFFFFF",
        "selection": "#315C88",
        "calendar_header": "#252E3A",
        "calendar_cell": "#1B222C",
        "calendar_grid": "#3A4554",
        "conflict_row": "#5A431C",
        "danger": "#FF6B6B",
    },
    "coastal_light": {
        "name": "Coastal Light",
        "background": "#E8F0F5",
        "surface": "#F7FAFC",
        "surface_alt": "#D7E5EE",
        "input": "#FFFFFF",
        "border": "#9CB6C7",
        "text": "#173247",
        "muted": "#526D80",
        "accent": "#287FA8",
        "accent_hover": "#3697C3",
        "accent_text": "#FFFFFF",
        "selection": "#B9DDF0",
        "calendar_header": "#C9DFEA",
        "calendar_cell": "#F2F7FA",
        "calendar_grid": "#ACC4D1",
        "conflict_row": "#FFE1A8",
        "danger": "#B3261E",
    },
    "radio_albena": {
        "name": "Radio Albena",
        "background": "#07153D",
        "surface": "#0B2455",
        "surface_alt": "#12346F",
        "input": "#06122F",
        "border": "#31558C",
        "text": "#F7FAFF",
        "muted": "#B9CBE5",
        "accent": "#FF9F43",
        "accent_hover": "#FFB466",
        "accent_text": "#17213A",
        "selection": "#245BA0",
        "calendar_header": "#102D64",
        "calendar_cell": "#0A1D48",
        "calendar_grid": "#2A4B7D",
        "conflict_row": "#6A451D",
        "danger": "#FF6B5E",
    },
    "color_wave": {
        "name": "Color Wave",
        "background": "#201A3D",
        "surface": "#30245A",
        "surface_alt": "#46357A",
        "input": "#17132D",
        "border": "#6B55A0",
        "text": "#FFF9FF",
        "muted": "#D8CBE8",
        "accent": "#2FD4C6",
        "accent_hover": "#64E5D9",
        "accent_text": "#102D32",
        "selection": "#7650B7",
        "calendar_header": "#3A286B",
        "calendar_cell": "#291F4B",
        "calendar_grid": "#604C8B",
        "conflict_row": "#70442B",
        "danger": "#FF7597",
    },
}


def get_theme(theme_id):
    return THEMES.get(theme_id, THEMES[DEFAULT_THEME])


def apply_theme(root, theme_id):
    theme = get_theme(theme_id)
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=theme["background"])

    style.configure(
        ".",
        background=theme["background"],
        foreground=theme["text"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "TFrame",
        background=theme["background"],
    )
    style.configure(
        "Surface.TFrame",
        background=theme["surface"],
    )
    style.configure(
        "TLabel",
        background=theme["background"],
        foreground=theme["text"],
    )
    style.configure(
        "TLabelFrame",
        background=theme["background"],
        foreground=theme["text"],
        bordercolor=theme["border"],
    )
    style.configure(
        "TLabelFrame.Label",
        background=theme["background"],
        foreground=theme["text"],
    )
    style.configure(
        "TButton",
        background=theme["surface_alt"],
        foreground=theme["text"],
        bordercolor=theme["border"],
        padding=(10, 6),
    )
    style.map(
        "TButton",
        background=[
            ("active", theme["accent"]),
            ("pressed", theme["accent_hover"]),
        ],
        foreground=[
            ("active", theme["accent_text"]),
            ("pressed", theme["accent_text"]),
        ],
    )
    style.configure(
        "Accent.TButton",
        background=theme["accent"],
        foreground=theme["accent_text"],
    )
    style.map(
        "Accent.TButton",
        background=[
            ("active", theme["accent_hover"]),
            ("pressed", theme["accent"]),
        ],
    )
    style.configure(
        "TEntry",
        fieldbackground=theme["input"],
        foreground=theme["text"],
        bordercolor=theme["border"],
        insertcolor=theme["text"],
    )
    style.configure(
        "TCombobox",
        fieldbackground=theme["input"],
        background=theme["surface_alt"],
        foreground=theme["text"],
        arrowcolor=theme["text"],
        bordercolor=theme["border"],
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", theme["input"])],
        foreground=[("readonly", theme["text"])],
        selectbackground=[("readonly", theme["selection"])],
        selectforeground=[("readonly", theme["text"])],
    )
    style.configure(
        "TCheckbutton",
        background=theme["background"],
        foreground=theme["text"],
    )
    style.map(
        "TCheckbutton",
        background=[("active", theme["background"])],
        foreground=[("active", theme["text"])],
    )
    style.configure(
        "TNotebook",
        background=theme["background"],
        bordercolor=theme["border"],
    )
    style.configure(
        "TNotebook.Tab",
        background=theme["surface"],
        foreground=theme["muted"],
        padding=(16, 8),
    )
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", theme["accent"]),
            ("active", theme["surface_alt"]),
        ],
        foreground=[
            ("selected", theme["accent_text"]),
            ("active", theme["text"]),
        ],
    )
    style.configure(
        "Treeview",
        background=theme["surface"],
        fieldbackground=theme["surface"],
        foreground=theme["text"],
        bordercolor=theme["border"],
        rowheight=26,
    )
    style.map(
        "Treeview",
        background=[("selected", theme["selection"])],
        foreground=[("selected", theme["text"])],
    )
    style.configure(
        "Treeview.Heading",
        background=theme["surface_alt"],
        foreground=theme["text"],
        bordercolor=theme["border"],
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "Treeview.Heading",
        background=[("active", theme["accent"])],
        foreground=[("active", theme["accent_text"])],
    )
    style.configure(
        "TScrollbar",
        background=theme["surface_alt"],
        troughcolor=theme["background"],
        bordercolor=theme["border"],
        arrowcolor=theme["text"],
    )
    style.configure(
        "Status.TLabel",
        background=theme["surface"],
        foreground=theme["muted"],
        bordercolor=theme["border"],
    )

    root.option_add("*Menu.background", theme["surface"])
    root.option_add("*Menu.foreground", theme["text"])
    root.option_add("*Menu.activeBackground", theme["accent"])
    root.option_add("*Menu.activeForeground", theme["accent_text"])
    root.option_add("*Menu.selectColor", theme["accent"])

    menu_name = root.cget("menu")

    if menu_name:
        try:
            _apply_menu_colors(
                root.nametowidget(menu_name),
                theme
            )
        except Exception:
            pass

    return theme


def _apply_menu_colors(menu, theme):
    menu.configure(
        background=theme["surface"],
        foreground=theme["text"],
        activebackground=theme["accent"],
        activeforeground=theme["accent_text"],
        selectcolor=theme["accent"],
    )

    last_index = menu.index("end")

    if last_index is None:
        return

    for index in range(last_index + 1):
        try:
            submenu_name = menu.entrycget(
                index,
                "menu"
            )
        except Exception:
            continue

        if not submenu_name:
            continue

        try:
            submenu = menu.nametowidget(
                submenu_name
            )
            _apply_menu_colors(
                submenu,
                theme
            )
        except Exception:
            continue
