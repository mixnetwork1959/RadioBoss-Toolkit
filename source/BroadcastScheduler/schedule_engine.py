# ==========================================
# Broadcast Scheduler
# Version 3.0.0
# schedule_engine.py
# ==========================================

from datetime import datetime, timedelta
from typing import List

from models import Event, RunTime


class ScheduleEngine:

    def __init__(self):
        self.week_start = None
        self.week_end = None

    def get_current_week(self, week_offset: int = 0):
        today = datetime.now()

        monday = today - timedelta(days=today.weekday())
        monday += timedelta(weeks=week_offset)
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)

        sunday = monday + timedelta(days=6)
        sunday = sunday.replace(hour=23, minute=59, second=59, microsecond=0)

        self.week_start = monday
        self.week_end = sunday

        return monday, sunday

    def decode_days(self, days: str) -> List[int]:
        result = []
        if len(days) != 7:
            return result

        mapping = [6, 0, 1, 2, 3, 4, 5]

        for index, value in enumerate(days):
            if value == "1":
                result.append(mapping[index])

        return sorted(result)

    def decode_hours(self, hours: str) -> List[int]:
        return [hour for hour, value in enumerate(hours) if value == "1"]

    def decode_minutes(self, minutes: str) -> List[int]:
        if not minutes:
            return [0]

        result = []
        for value in minutes.split(","):
            value = value.strip()
            if value:
                result.append(int(value))
        return result

    def decode_seconds(self, seconds: int) -> int:
        return seconds

    def _generate_event(self, event: Event) -> List[RunTime]:
        runtimes: List[RunTime] = []

        if not event.enabled:
            return runtimes

        if event.time_type != 1:
            return runtimes

        days = self.decode_days(event.days)
        hours = self.decode_hours(event.hours)
        minutes = self.decode_minutes(event.minutes)
        second = self.decode_seconds(event.seconds)

        for weekday in days:
            current_day = self.week_start + timedelta(days=weekday)

            for hour in hours:
                for minute in minutes:
                    start = current_day.replace(
                        hour=hour,
                        minute=minute,
                        second=second,
                        microsecond=0
                    )

                    runtimes.append(
                        RunTime(
                            event=event,
                            start=start,
                            end=start
                        )
                    )

        return runtimes

    def generate(
        self,
        events: List[Event],
        week_offset: int = 0
    ) -> List[RunTime]:

        self.get_current_week(week_offset)

        runtimes: List[RunTime] = []

        for event in events:
            event_runtimes = self._generate_event(event)
            runtimes.extend(event_runtimes)

        runtimes.sort(key=lambda rt: rt.start)

        for current, nxt in zip(runtimes, runtimes[1:]):
            current.end = nxt.start

        if runtimes:
            runtimes[-1].end = self.week_end

        return runtimes
