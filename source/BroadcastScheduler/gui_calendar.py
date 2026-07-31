# ==========================================
# Broadcast Scheduler
# Version 4.4.0
# gui_calendar.py
# ==========================================

import tkinter as tk
from tkinter import ttk, messagebox
from scheduler_i18n import language


LEFT = 70
TOP = 35

DAY_WIDTH = 210
HOUR_HEIGHT = 220

DAY_NAMES={"en":("Mon","Tue","Wed","Thu","Fri","Sat","Sun"),"de":("Mo","Di","Mi","Do","Fr","Sa","So"),"nl":("Ma","Di","Wo","Do","Vr","Za","Zo"),"bg":("Пон","Вт","Ср","Чет","Пет","Съб","Нед")}
DIALOG={"en":("Yes","No","Event","Group","End","Conflict","Event Details"),"de":("Ja","Nein","Ereignis","Gruppe","Ende","Konflikt","Ereignisdetails"),"nl":("Ja","Nee","Gebeurtenis","Groep","Einde","Conflict","Gebeurtenisdetails"),"bg":("Да","Не","Събитие","Група","Край","Конфликт","Детайли за събитието")}




# =====================================================
# RadioBOSS Color Conversion
# =====================================================

def radioboss_color_to_hex(
    value,
    fallback="#EEEEEE"
):
    """
    Wandelt einen RadioBOSS-/Windows-COLORREF-Wert in #RRGGBB um.

    COLORREF speichert Farben als 0x00BBGGRR.
    """

    try:
        color_value = int(
            str(value).strip()
        )
    except (TypeError, ValueError):
        return fallback

    # -1 bedeutet in RadioBOSS/Windows häufig:
    # keine feste Farbe bzw. Standardfarbe.
    if color_value < 0:
        return fallback

    red = color_value & 0xFF
    green = (color_value >> 8) & 0xFF
    blue = (color_value >> 16) & 0xFF

    return f"#{red:02X}{green:02X}{blue:02X}"


def get_contrast_text_color(
    background
):
    """
    Liefert Schwarz oder Weiß passend zur Hintergrundfarbe.
    """

    try:
        red = int(background[1:3], 16)
        green = int(background[3:5], 16)
        blue = int(background[5:7], 16)
    except (TypeError, ValueError, IndexError):
        return "#000000"

    brightness = (
        (red * 299) +
        (green * 587) +
        (blue * 114)
    ) / 1000

    if brightness >= 140:
        return "#000000"

    return "#FFFFFF"


# =====================================================
# Create Calendar
# =====================================================

def create_calendar(parent, theme):

    frame = ttk.Frame(parent)

    frame.pack(
        fill="both",
        expand=True
    )

    vscroll = ttk.Scrollbar(
        frame,
        orient="vertical"
    )

    vscroll.pack(
        side="right",
        fill="y"
    )

    hscroll = ttk.Scrollbar(
        frame,
        orient="horizontal"
    )

    hscroll.pack(
        side="bottom",
        fill="x"
    )

    canvas = tk.Canvas(
        frame,
        bg=theme["background"],
        highlightthickness=0,
        yscrollcommand=vscroll.set,
        xscrollcommand=hscroll.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    vscroll.config(
        command=canvas.yview
    )

    hscroll.config(
        command=canvas.xview
    )

    return (
        frame,
        canvas,
        vscroll,
        hscroll
    )
# =====================================================
# Draw Header
# =====================================================

def draw_header(
    canvas,
    total_width,
    theme
):

    for index, day in enumerate(DAY_NAMES.get(language(), DAY_NAMES["en"])):

        x = LEFT + (index * DAY_WIDTH)

        canvas.create_rectangle(
            x,
            0,
            x + DAY_WIDTH,
            TOP,
            fill=theme["calendar_header"],
            outline=theme["calendar_grid"]
        )

        canvas.create_text(
            x + DAY_WIDTH / 2,
            TOP / 2,
            text=day,
            font=("Segoe UI", 12, "bold"),
            fill=theme["text"]
        )
# =====================================================
# Draw Hours
# =====================================================

def draw_hours(
    canvas,
    total_width,
    theme
):

    for hour in range(24):

        y = TOP + (hour * HOUR_HEIGHT)

        canvas.create_text(
            35,
            y + 10,
            text=f"{hour:02d}:00",
            font=("Segoe UI", 10, "bold"),
            fill=theme["text"]
        )

        canvas.create_line(
            LEFT,
            y,
            total_width,
            y,
            fill=theme["calendar_grid"]
        )

    canvas.create_line(
        LEFT,
        TOP + (24 * HOUR_HEIGHT),
        total_width,
        TOP + (24 * HOUR_HEIGHT),
        fill=theme["calendar_grid"]
    )
# =====================================================
# Draw Day Lines
# =====================================================

def draw_day_lines(
    canvas,
    total_height,
    theme
):

    for day in range(8):

        x = LEFT + (day * DAY_WIDTH)

        canvas.create_line(
            x,
            TOP,
            x,
            total_height,
            fill=theme["calendar_grid"]
        )


# =====================================================
# Show Event Details
# =====================================================

def show_event_details(rt):

    event_name = getattr(
        rt.event,
        "name",
        "Unknown"
    )

    group = getattr(
        rt.event,
        "group",
        ""
    )

    event_id = getattr(
        rt.event,
        "id",
        ""
    )

    back_color = getattr(
        rt.event,
        "back_color",
        ""
    )

    font_color = getattr(
        rt.event,
        "font_color",
        ""
    )

    start_text = (
        rt.start.strftime("%A, %d.%m.%Y %H:%M:%S")
        if getattr(rt, "start", None)
        else "-"
    )

    end_value = getattr(
        rt,
        "end",
        None
    )

    end_text = (
        end_value.strftime("%A, %d.%m.%Y %H:%M:%S")
        if end_value
        else "-"
    )

    labels=DIALOG.get(language(),DIALOG["en"])
    conflict = (
        labels[0]
        if getattr(rt, "conflict", False)
        else labels[1]
    )

    details = (
        f"{labels[2]}: {event_name}\n"
        f"ID: {event_id or '-'}\n"
        f"{labels[3]}: {group or '-'}\n\n"
        f"Start: {start_text}\n"
        f"{labels[4]}: {end_text}\n"
        f"{labels[5]}: {conflict}\n\n"
        f"BackColor: {back_color or '-'}\n"
        f"FontColor: {font_color or '-'}"
    )

    messagebox.showinfo(
        labels[6],
        details
    )


# =====================================================
# Draw Events
# =====================================================

def draw_events(
    canvas,
    runtimes,
    theme
):

    if not runtimes:
        return

    week_start = runtimes[0].start.date()

    hour_events = {}

    for rt in runtimes:

        day = (
            rt.start.date() -
            week_start
        ).days

        if day < 0 or day > 6:
            continue

        key = (
            day,
            rt.start.hour
        )

        hour_events.setdefault(
            key,
            []
        ).append(rt)

    for (day, hour), events in hour_events.items():

        x = LEFT + (day * DAY_WIDTH) + 5
        y = TOP + (hour * HOUR_HEIGHT) + 5

        canvas.create_rectangle(
            x,
            y,
            x + DAY_WIDTH - 10,
            y + HOUR_HEIGHT - 10,
            fill=theme["calendar_cell"],
            outline=theme["calendar_grid"]
        )

        canvas.create_text(
            x + 6,
            y + 6,
            anchor="nw",
            text=f"{hour:02d}:00",
            font=("Segoe UI", 12, "bold"),
            fill=theme["text"]
        )

        yy = y + 28

        visible_events = 0

        for rt in events:

            color = radioboss_color_to_hex(
                getattr(
                    rt.event,
                    "back_color",
                    ""
                ),
                fallback="#EEEEEE"
            )

            font_color_value = getattr(
                rt.event,
                "font_color",
                ""
            )

            font_color = radioboss_color_to_hex(
                font_color_value,
                fallback=get_contrast_text_color(
                    color
                )
            )

            if getattr(rt, "conflict", False):

                outline = theme["danger"]
                width = 3

            else:

                outline = theme["calendar_grid"]
                width = 1

            event_tag = (
                f"event_{day}_{hour}_{visible_events}"
            )

            canvas.create_rectangle(
                x + 4,
                yy,
                x + DAY_WIDTH - 14,
                yy + 18,
                fill=color,
                outline=outline,
                width=width,
                tags=(event_tag,)
            )

            canvas.create_text(
                x + 8,
                yy + 9,
                anchor="w",
                text=f"{rt.start:%H:%M}  {rt.event.name}",
                font=("Segoe UI", 10),
                fill=font_color,
                tags=(event_tag,)
            )

            canvas.tag_bind(
                event_tag,
                "<Double-Button-1>",
                lambda event, runtime=rt: show_event_details(
                    runtime
                )
            )

            canvas.tag_bind(
                event_tag,
                "<Enter>",
                lambda event: canvas.configure(
                    cursor="hand2"
                )
            )

            canvas.tag_bind(
                event_tag,
                "<Leave>",
                lambda event: canvas.configure(
                    cursor=""
                )
            )

            yy += 24

            visible_events += 1

            if yy > y + HOUR_HEIGHT - 20:

                hidden = (
                    len(events)
                    - visible_events
                )

                if hidden > 0:

                    canvas.create_text(
                        x + 8,
                        yy,
                        anchor="w",
                        text=f"(+{hidden})",
                        font=("Segoe UI", 8, "bold"),
                        fill="red"
                    )

                break
# =====================================================
# Draw Calendar
# =====================================================

def draw_calendar(
    canvas,
    runtimes,
    theme
):
    """
    Draw the weekly calendar.
    """

    canvas.delete("all")
    canvas.configure(bg=theme["background"])

    total_width = LEFT + (len(DAY_NAMES["en"]) * DAY_WIDTH)
    total_height = TOP + (24 * HOUR_HEIGHT)

    canvas.configure(
        scrollregion=(
            0,
            0,
            total_width,
            total_height
        )
    )

    draw_header(
        canvas,
        total_width,
        theme
    )

    draw_hours(
        canvas,
        total_width,
        theme
    )

    draw_day_lines(
        canvas,
        total_height,
        theme
    )

    draw_events(
        canvas,
        runtimes,
        theme
    )                                
