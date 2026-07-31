# ==========================================
# Broadcast Scheduler
# Version 4.4.0
# gui_treeview.py
# ==========================================

from tkinter import ttk
from scheduler_i18n import tr


# =====================================================
# Create TreeView
# =====================================================

def create_treeview(parent):

    frame = ttk.Frame(parent)

    frame.pack(
        fill="both",
        expand=True,
        padx=6,
        pady=6
    )

    columns = (
        "Status", "Start", "Group", "Event"
    )

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )

    # -------------------------------------------------
    # Scrollbars
    # -------------------------------------------------

    vsb = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    hsb = ttk.Scrollbar(
        frame,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set
    )

    # -------------------------------------------------
    # Row Tags
    # -------------------------------------------------

    tree.tag_configure(
        "conflict",
        background="#6A451D"
    )

    # -------------------------------------------------
    # Headings
    # -------------------------------------------------

    for column in columns:

        tree.heading(
            column,
            text={"Status":tr("status"),"Start":tr("start"),"Group":tr("group").rstrip(":"),"Event":tr("event")}[column]
        )

    # -------------------------------------------------
    # Columns
    # -------------------------------------------------

    tree.column(
        "Status",
        width=90,
        anchor="center"
    )

    tree.column(
        "Start",
        width=190,
        anchor="center"
    )

    tree.column(
        "Group",
        width=220,
        anchor="w"
    )

    tree.column(
        "Event",
        width=820,
        anchor="w"
    )

    # -------------------------------------------------
    # Layout
    # -------------------------------------------------

    tree.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    vsb.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    hsb.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    frame.rowconfigure(
        0,
        weight=1
    )

    frame.columnconfigure(
        0,
        weight=1
    )

    return (
        frame,
        tree,
        columns,
        vsb,
        hsb
    )
