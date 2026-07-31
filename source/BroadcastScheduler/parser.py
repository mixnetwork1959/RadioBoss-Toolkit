# ==========================================
# Broadcast Scheduler
# Version 3.0.0
# parser.py
# ==========================================

import os


DAY_NAMES = [
    "Su",
    "Mo",
    "Tu",
    "We",
    "Th",
    "Fr",
    "Sa"
]


# =====================================================
# Decode Days
# =====================================================

def decode_days(days):
    """
    Wandelt die RadioBOSS-Tagesmaske in Tagesnamen um.

    Beispiel:
        1111111 -> ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
    """

    result = []

    for index, value in enumerate(days):

        if index >= len(DAY_NAMES):
            break

        if value == "1":
            result.append(DAY_NAMES[index])

    return result


# =====================================================
# Decode Hours
# =====================================================

def decode_hours(hours):
    """
    Wandelt die RadioBOSS-Stundenmaske in Stunden um.

    Beispiel:
        000000111100000000000000 -> [6, 7, 8, 9]
    """

    result = []

    for hour, value in enumerate(hours[:24]):

        if value == "1":
            result.append(hour)

    return result


# =====================================================
# Build Time Blocks
# =====================================================

def build_time_blocks(hour_list):
    """
    Wandelt eine Stundenliste in zusammenhängende Zeitblöcke um.

    Beispiele:

        [6, 7, 8, 9]
            -> [("06:00", "10:00")]

        [22, 23, 0, 1, 2, 3, 4, 5]
            -> [("22:00", "06:00")]

        [0, 1, ..., 23]
            -> [("00:00", "24:00")]
    """

    if not hour_list:
        return []

    unique_hours = sorted(set(hour_list))

    if len(unique_hours) == 24:
        return [("00:00", "24:00")]

    # Nachtblock über Mitternacht
    if 0 in unique_hours and 23 in unique_hours:

        late_hours = [
            hour
            for hour in unique_hours
            if hour >= 12
        ]

        early_hours = [
            hour
            for hour in unique_hours
            if hour < 12
        ]

        if late_hours and early_hours:

            start = min(late_hours)
            end = max(early_hours) + 1

            return [
                (
                    f"{start:02d}:00",
                    f"{end:02d}:00"
                )
            ]

    blocks = []

    start = unique_hours[0]
    previous = unique_hours[0]

    for hour in unique_hours[1:]:

        if hour == previous + 1:
            previous = hour
            continue

        blocks.append(
            (
                f"{start:02d}:00",
                f"{previous + 1:02d}:00"
            )
        )

        start = hour
        previous = hour

    blocks.append(
        (
            f"{start:02d}:00",
            f"{previous + 1:02d}:00"
        )
    )

    return blocks


# =====================================================
# Finalize Event
# =====================================================

def finalize_event(event):
    """
    Ergänzt die berechneten Felder eines eingelesenen Events.

    Alle originalen Schlüssel aus der SDL-Datei bleiben erhalten.
    """

    if event is None:
        return None

    days = event.get(
        "Days",
        ""
    )

    hours = event.get(
        "Hours",
        ""
    )

    event["DayList"] = decode_days(days)
    event["HourList"] = decode_hours(hours)
    event["TimeBlocks"] = build_time_blocks(
        event["HourList"]
    )

    return event


# =====================================================
# Load Events
# =====================================================

def load_events(filename):
    """
    Liest alle Events aus einer RadioBOSS-SDL-Datei.

    Anders als die frühere Version übernimmt dieser Parser jedes
    vorhandene Schlüssel=Wert-Paar. Dadurch bleiben unter anderem
    ID, BackColor, FontColor, Priority und zukünftige RadioBOSS-
    Felder automatisch erhalten.
    """

    if not os.path.exists(filename):
        raise FileNotFoundError(filename)

    events = []
    current = None

    with open(
        filename,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        for raw_line in file:

            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("[event"):

                if current is not None:

                    finalized = finalize_event(
                        current
                    )

                    if finalized is not None:
                        events.append(finalized)

                current = {}

                continue

            if current is None:
                continue

            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1
            )

            key = key.strip()
            value = value.strip()

            if not key:
                continue

            current[key] = value

    if current is not None:

        finalized = finalize_event(
            current
        )

        if finalized is not None:
            events.append(finalized)

    return events
