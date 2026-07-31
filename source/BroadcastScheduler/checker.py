# ==========================================
# Broadcast Scheduler
# Version 3.0.0
# checker.py
# ==========================================

def time_to_minutes(t):
    """'06:00' -> 360"""
    h, m = map(int, t.split(":"))
    return h * 60 + m


def overlap(start1, end1, start2, end2):
    """
    Prüft, ob sich zwei Zeiträume überschneiden.
    Gibt (True, Start, Ende) zurück.
    """

    s1 = time_to_minutes(start1)
    e1 = time_to_minutes(end1)

    s2 = time_to_minutes(start2)
    e2 = time_to_minutes(end2)

    start = max(s1, s2)
    end = min(e1, e2)

    if start < end:

        return (
            True,
            f"{start//60:02d}:{start%60:02d}",
            f"{end//60:02d}:{end%60:02d}"
        )

    return False, "", ""


def check_overlaps(events):

    result = []

    # Nur aktive Events
    active = [
        e for e in events
        if e["EnabledEvent"] == "1"
    ]

    for i in range(len(active)):

        event1 = active[i]

        for j in range(i + 1, len(active)):

            event2 = active[j]

            # gemeinsame Tage
            days = sorted(
                set(event1["DayList"]) &
                set(event2["DayList"])
            )

            if not days:
                continue

            overlaps = []

            for start1, end1 in event1["TimeBlocks"]:

                for start2, end2 in event2["TimeBlocks"]:

                    ok, ov_start, ov_end = overlap(
                        start1,
                        end1,
                        start2,
                        end2
                    )

                    if ok:

                        overlaps.append({
                            "event1_time": f"{start1} - {end1}",
                            "event2_time": f"{start2} - {end2}",
                            "overlap": f"{ov_start} - {ov_end}"
                        })

            if overlaps:

                result.append({

                    # IDs (neu)
                    "event1_id": event1["ID"],
                    "event2_id": event2["ID"],

                    # Namen (für aktuelle GUI)
                    "event1": event1["TaskName"],
                    "event2": event2["TaskName"],

                    "days": days,

                    # alle Überschneidungen
                    "overlaps": overlaps,

                    # Kompatibilität zur bisherigen Version
                    "event1_time": overlaps[0]["event1_time"],
                    "event2_time": overlaps[0]["event2_time"],
                    "overlap": overlaps[0]["overlap"]

                })

    return result