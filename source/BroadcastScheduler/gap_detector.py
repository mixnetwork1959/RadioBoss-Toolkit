# ==========================================
# Broadcast Scheduler
# Version 3.0.0
# gap_detector.py
# ==========================================

from datetime import timedelta


GAP_THRESHOLD = timedelta(seconds=30)


def detect_gaps(runtimes):

    gaps = []

    if len(runtimes) < 2:
        return gaps

    runtimes = sorted(
        runtimes,
        key=lambda rt: rt.start
    )

    for current, nxt in zip(runtimes, runtimes[1:]):

        current_end = current.end

        gap = nxt.start - current_end

        if gap >= GAP_THRESHOLD:

            gaps.append({
                "from": current,
                "to": nxt,
                "duration": gap
            })

    return gaps