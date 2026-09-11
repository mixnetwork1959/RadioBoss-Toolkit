# ==========================================
# Broadcast Scheduler
# Version 4.5.1
# schedule_engine.py
# ==========================================

from datetime import datetime, timedelta
from typing import List, Optional
import re

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
                try:
                    minute = int(value)
                except ValueError:
                    continue
                if 0 <= minute <= 59:
                    result.append(minute)
        return result or [0]

    def decode_seconds(self, seconds: int) -> int:
        try:
            return max(0, min(59, int(seconds)))
        except (TypeError, ValueError):
            return 0

    def _parse_datetime(self, value: str) -> Optional[datetime]:
        """Parse RadioBOSS DateTime values without depending on Windows locale."""

        value = str(value or "").strip()
        if not value:
            return None

        # ISO values, including the common ``YYYY-MM-DD HH:MM:SS`` form.
        try:
            return datetime.fromisoformat(value.replace("T", " "))
        except ValueError:
            pass

        formats = (
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
        )

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        # Final fallback for values containing a localized date plus extra text.
        match = re.search(
            r"(?P<day>\d{1,2})[.\-/](?P<month>\d{1,2})[.\-/](?P<year>\d{4})"
            r"(?:\s+(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(?::(?P<second>\d{1,2}))?)?",
            value,
        )
        if match:
            try:
                return datetime(
                    int(match.group("year")),
                    int(match.group("month")),
                    int(match.group("day")),
                    int(match.group("hour") or 0),
                    int(match.group("minute") or 0),
                    int(match.group("second") or 0),
                )
            except ValueError:
                return None

        return None

    def _times_for_day(self, event: Event, day: datetime) -> List[RunTime]:
        """Create all configured hour/minute runtimes for one calendar day."""

        runtimes: List[RunTime] = []
        hours = self.decode_hours(event.hours)
        minutes = self.decode_minutes(event.minutes)
        second = self.decode_seconds(event.seconds)

        # Date-specific RadioBOSS entries normally still carry the hour/minute
        # masks. If a file does not, fall back to the time stored in DateTime.
        if not hours:
            parsed = self._parse_datetime(event.datetime)
            if parsed is None:
                return runtimes
            hours = [parsed.hour]
            minutes = [parsed.minute]
            second = parsed.second

        for hour in hours:
            for minute in minutes:
                start = day.replace(
                    hour=hour,
                    minute=minute,
                    second=second,
                    microsecond=0,
                )
                runtimes.append(
                    RunTime(
                        event=event,
                        start=start,
                        end=start,
                    )
                )

        return runtimes

    def _generate_dated_event(self, event: Event) -> List[RunTime]:
        """Generate a UseDate event only when its real date is in this week."""

        parsed = self._parse_datetime(event.datetime)
        if parsed is None:
            return []

        candidates: List[datetime] = []

        if event.every_year:
            # A displayed week can span New Year, so test both calendar years.
            for year in sorted({self.week_start.year, self.week_end.year}):
                try:
                    candidates.append(parsed.replace(year=year))
                except ValueError:
                    # Example: 29 February in a non-leap year.
                    continue
        else:
            candidates.append(parsed)

        runtimes: List[RunTime] = []
        for candidate in candidates:
            day = candidate.replace(hour=0, minute=0, second=0, microsecond=0)
            if self.week_start <= day <= self.week_end:
                runtimes.extend(self._times_for_day(event, day))

        return runtimes

    def _generate_event(self, event: Event) -> List[RunTime]:
        runtimes: List[RunTime] = []

        if not event.enabled:
            return runtimes

        if event.time_type != 1:
            return runtimes

        # IMPORTANT: RadioBOSS date-specific events must not be expanded from
        # their weekday mask. Doing that made unrelated monthly/yearly events
        # appear on the same weekday and created false conflicts.
        if event.use_date:
            return self._generate_dated_event(event)

        days = self.decode_days(event.days)

        for weekday in days:
            current_day = self.week_start + timedelta(days=weekday)
            runtimes.extend(self._times_for_day(event, current_day))

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
