# ==========================================
# Broadcast Scheduler
# Public Calendar Test
# ==========================================

from config import load_settings
from database import Database
from scheduler_controller import SchedulerController
from public_calendar_engine import PublicCalendarEngine


def main():

    settings = load_settings()

    database = Database(settings)

    events = database.load_events()

    controller = SchedulerController(events)

    runtimes = controller.refresh()

    engine = PublicCalendarEngine()

    blocks = engine.detect(runtimes)

    rows = engine.to_rows(blocks)

    print()
    print("=" * 70)
    print("PUBLIC CALENDAR CANDIDATES")
    print("=" * 70)

    for row in rows:

        print(
            f"{row['day']:<10} "
            f"{row['start']}-{row['end']}  "
            f"{row['internal_name']}  "
            f"[{row['confidence']}]"
        )

    print()
    print(f"Detected blocks: {len(rows)}")
    print("=" * 70)


if __name__ == "__main__":
    main()