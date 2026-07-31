# ==========================================
# Broadcast Scheduler
# Version 4.4.0
# gui_statusbar.py
# ==========================================

from tkinter import ttk
from scheduler_i18n import tr


# =====================================================
# Create Status Bar
# =====================================================

def create_statusbar(root):

    status = ttk.Label(
        root,
        text="",
        anchor="w",
        relief="sunken",
        padding=4,
        style="Status.TLabel"
    )

    status.pack(
        fill="x",
        side="bottom"
    )

    return status


# =====================================================
# Refresh Status Bar
# =====================================================

def refresh_statusbar(status, runtimes):

    event_count = len({rt.event.id for rt in runtimes})
    runtime_count = len(runtimes)

    conflict_count = sum(
        1
        for rt in runtimes
        if getattr(rt, "conflict", False)
    )

    ok_count = runtime_count - conflict_count

    if runtimes:
        week_start = runtimes[0].start.strftime("%d.%m.%Y")
        week_end = runtimes[-1].start.strftime("%d.%m.%Y")
    else:
        week_start = "-"
        week_end = "-"

    status.config(
        text=(
            f"OK: {ok_count}    |    "
            f"{tr('conflicts')}: {conflict_count}    |    "
            f"{tr('events')}: {event_count}    |    "
            f"{tr('runtimes')}: {runtime_count}    |    "
            f"{tr('week')}: {week_start} - {week_end}"
        )
    )
