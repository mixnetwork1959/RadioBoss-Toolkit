# ==========================================
# Broadcast Scheduler
# Version 4.5.0
# gui.py
# ==========================================

import tkinter as tk
from tkinter import ttk

from gui_tree import (
    sort_column,
    populate_tree
)
from gui_statusbar import (
    create_statusbar,
    refresh_statusbar
)
from gui_filter import (
    create_filter_bar
)
from gui_toolbar import (
    create_toolbar
)
from gui_menu import (
    create_menu
)
from gui_treeview import (
    create_treeview
)
from gui_calendar import (
    create_calendar,
    draw_calendar
)
from gui_public_calendar import (
    PublicCalendarTab
)
from config import save_settings
from theme_manager import (
    THEMES,
    DEFAULT_THEME,
    apply_theme
)
from scheduler_i18n import tr


# =====================================================
# Main Window
# =====================================================

def show_events(controller, runtimes, settings):

    root = tk.Tk()

    root.title("Broadcast Scheduler 4.5.1")
    root.geometry("1600x900")

    theme_id = settings.get(
        "theme",
        DEFAULT_THEME
    )

    if theme_id not in THEMES:
        theme_id = DEFAULT_THEME

    theme_var = tk.StringVar(
        value=theme_id
    )

    current_theme = apply_theme(
        root,
        theme_id
    )

    # =====================================================
    # Toolbar
    # =====================================================

    (
        toolbar,
        btn_refresh,
        btn_prev,
        btn_today,
        btn_next,
    ) = create_toolbar(root)

    # =====================================================
    # Filter Bar
    # =====================================================

    (
        filter_frame,
        search_var,
        group_var,
        group_combo,
        conflict_var
    ) = create_filter_bar(root)

    # =====================================================
    # Notebook
    # =====================================================

    notebook = ttk.Notebook(root)

    notebook.pack(
        fill="both",
        expand=True,
        padx=6,
        pady=6
    )

    # =====================================================
    # Events Tab
    # =====================================================

    events_tab = ttk.Frame(notebook)

    notebook.add(
        events_tab,
        text=tr("events")
    )

    # =====================================================
    # Calendar Tab
    # =====================================================

    calendar_tab = ttk.Frame(notebook)

    notebook.add(
        calendar_tab,
        text=tr("calendar")
    )


    # =====================================================
    # Public Calendar Tab
    # =====================================================

    public_calendar_tab = ttk.Frame(notebook)

    notebook.add(
        public_calendar_tab,
        text=tr("public")
    )

    # =====================================================
    # Calendar
    # =====================================================

    (
        calendar_frame,
        calendar_canvas,
        calendar_vscroll,
        calendar_hscroll
    ) = create_calendar(
        calendar_tab,
        current_theme
    )

    # =====================================================
    # TreeView
    # =====================================================

    (
        frame,
        tree,
        columns,
        vsb,
        hsb
    ) = create_treeview(events_tab)


    # =====================================================
    # Public Calendar
    # =====================================================

    public_calendar = PublicCalendarTab(
        public_calendar_tab,
        controller.events,
        runtimes,
        settings=settings
    )

    # Sortierung aktivieren

    for column in columns:

        tree.heading(
            column,
            text=column,
            command=lambda c=column: sort_column(
                tree,
                c,
                False
            )
        )

    # =====================================================
    # Status Bar
    # =====================================================

    status = create_statusbar(root)

    # =====================================================
    # Helper Functions
    # =====================================================

    def update_group_filter():

        current_group = group_var.get()

        groups = [
            tr("all"),
            *sorted({
                rt.event.group
                for rt in runtimes
                if getattr(rt.event, "group", "")
            })
        ]

        group_combo.configure(
            values=groups
        )

        if current_group in groups:
            group_var.set(current_group)
        else:
            group_var.set(tr("all"))

    def refresh_tree(event=None):

        populate_tree(
            tree,
            runtimes,
            group_var.get(),
            conflict_var.get(),
            search_var.get()
        )

    def redraw_calendar(event=None):

        draw_calendar(
            calendar_canvas,
            runtimes,
            current_theme
        )

    def update_gui():

        update_group_filter()
        refresh_tree()
        redraw_calendar()

        refresh_statusbar(
            status,
            runtimes
        )

    # =====================================================
    # GUI Commands
    # =====================================================

    def refresh_gui(event=None):

        nonlocal runtimes

        runtimes = controller.refresh()

        update_gui()

    def previous_week():

        nonlocal runtimes

        runtimes = controller.previous_week()

        update_gui()

    def current_week():

        nonlocal runtimes

        runtimes = controller.current_week()

        update_gui()

    def next_week():

        nonlocal runtimes

        runtimes = controller.next_week()

        update_gui()

    def show_calendar():

        notebook.select(calendar_tab)
        redraw_calendar()

    def change_theme():

        nonlocal current_theme

        selected_theme = theme_var.get()

        if selected_theme not in THEMES:
            selected_theme = DEFAULT_THEME
            theme_var.set(selected_theme)

        current_theme = apply_theme(
            root,
            selected_theme
        )

        settings["theme"] = selected_theme
        save_settings(settings)

        tree.tag_configure(
            "conflict",
            background=current_theme["conflict_row"],
            foreground=current_theme["text"]
        )

        public_calendar.apply_theme(
            current_theme
        )

        redraw_calendar()

    # =====================================================
    # Connect Toolbar Buttons
    # =====================================================

    btn_refresh.configure(
        command=refresh_gui
    )

    btn_prev.configure(
        command=previous_week
    )

    btn_today.configure(
        command=current_week
    )

    btn_next.configure(
        command=next_week
    )

    # =====================================================
    # Create and Connect Menu
    # =====================================================

    (
        menubar,
        file_menu,
        view_menu,
        theme_menu
    ) = create_menu(
        root,
        refresh_gui,
        theme_var,
        change_theme,
        THEMES
    )

    change_theme()

    # =====================================================
    # Filter Events
    # =====================================================

    group_combo.bind(
        "<<ComboboxSelected>>",
        refresh_tree
    )

    conflict_var.trace_add(
        "write",
        lambda *args: refresh_tree()
    )

    search_var.trace_add(
        "write",
        lambda *args: refresh_tree()
    )

    # =====================================================
    # Calendar Mouse Wheel
    # =====================================================

    calendar_canvas.bind(
        "<MouseWheel>",
        lambda event: calendar_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )
    )

    calendar_canvas.bind(
        "<Configure>",
        redraw_calendar
    )

    # =====================================================
    # Initial Display
    # =====================================================

    update_gui()

    def scroll_to_current_time():

        from datetime import datetime

        current_hour = datetime.now().hour

        y = max(
            0,
            ((current_hour - 1) * 220) / (
                35 + (24 * 220)
            )
        )

        calendar_canvas.yview_moveto(y)

    root.after(
        200,
        scroll_to_current_time
    )

    root.after(
        100,
        redraw_calendar
    )

    # =====================================================
    # Start GUI
    # =====================================================

    root.mainloop()
