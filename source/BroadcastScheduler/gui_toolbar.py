# ==========================================
# Broadcast Scheduler
# Version 4.4.0
# gui_toolbar.py
# ==========================================

from tkinter import ttk
from scheduler_i18n import tr


# =====================================================
# Create Toolbar
# =====================================================

def create_toolbar(root):

    toolbar = ttk.Frame(root)

    toolbar.pack(
        fill="x",
        padx=6,
        pady=6
    )

    btn_refresh = ttk.Button(
        toolbar,
        text="🔄 " + tr("refresh"),
        style="Accent.TButton"
    )

    btn_refresh.pack(
        side="left",
        padx=2
    )

    btn_prev = ttk.Button(
        toolbar,
        text=tr("previous")
    )

    btn_prev.pack(
        side="left",
        padx=2
    )

    btn_today = ttk.Button(
        toolbar,
        text=tr("today")
    )

    btn_today.pack(
        side="left",
        padx=2
    )

    btn_next = ttk.Button(
        toolbar,
        text=tr("next")
    )

    btn_next.pack(
        side="left",
        padx=2
    )

    return (
        toolbar,
        btn_refresh,
        btn_prev,
        btn_today,
        btn_next,
    )
