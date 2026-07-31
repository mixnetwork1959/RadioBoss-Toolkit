# ==========================================
# Broadcast Scheduler
# Version 4.4.0
# gui_filter.py
# ==========================================

import tkinter as tk
from tkinter import ttk
from scheduler_i18n import tr


# =====================================================
# Create Filter Bar
# =====================================================

def create_filter_bar(root):

    filter_frame = ttk.Frame(root)

    filter_frame.pack(
        fill="x",
        padx=6,
        pady=(0, 6)
    )

    # -------------------------------------------------
    # Search
    # -------------------------------------------------

    ttk.Label(
        filter_frame,
        text=tr("search")
    ).pack(
        side="left",
        padx=(0, 5)
    )

    search_var = tk.StringVar()

    search_entry = ttk.Entry(
        filter_frame,
        textvariable=search_var,
        width=35
    )

    search_entry.pack(
        side="left",
        padx=(0, 15)
    )

    # -------------------------------------------------
    # Group
    # -------------------------------------------------

    ttk.Label(
        filter_frame,
        text=tr("group")
    ).pack(
        side="left",
        padx=(0, 5)
    )

    group_var = tk.StringVar(value=tr("all"))

    group_combo = ttk.Combobox(
        filter_frame,
        textvariable=group_var,
        values=[tr("all")],
        state="readonly",
        width=20
    )

    group_combo.current(0)

    group_combo.pack(
        side="left",
        padx=(0, 15)
    )

    # -------------------------------------------------
    # Only Conflicts
    # -------------------------------------------------

    conflict_var = tk.BooleanVar(value=False)

    ttk.Checkbutton(
        filter_frame,
        text=tr("conflicts_only"),
        variable=conflict_var
    ).pack(
        side="left"
    )

    return (
        filter_frame,
        search_var,
        group_var,
        group_combo,
        conflict_var
    )
