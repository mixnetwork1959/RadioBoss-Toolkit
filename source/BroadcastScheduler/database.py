# ==========================================
# Broadcast Scheduler
# Version 3.0.0
# database.py
#
# Änderungen:
# - SDL-Datei wird nur noch durch parser.py gelesen
# - database.py erstellt nur noch Event-Objekte
# - BackColor und FontColor werden übernommen
# - Alle originalen SDL-Felder bleiben in raw_data erhalten
# ==========================================

import os
from typing import List, Dict, Any

from models import Event
from parser import load_events as parse_sdl_events


# =====================================================
# Conversion Helpers
# =====================================================

def to_bool(value: Any) -> bool:
    """
    RadioBOSS speichert boolesche Werte üblicherweise als 0 oder 1.
    """

    return str(value).strip() == "1"


def to_int(value: Any, default: int = 0) -> int:
    """
    Wandelt einen SDL-Wert sicher in Integer um.
    """

    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


# =====================================================
# Database
# =====================================================

class Database:

    def __init__(self, settings):

        self.settings = settings
        self.filename = settings.get(
            "admin_sdl",
            ""
        )

    # =================================================
    # Build Event
    # =================================================

    def _build_event(
        self,
        data: Dict[str, str]
    ) -> Event:

        return Event(
            id=data.get(
                "ID",
                ""
            ),

            name=data.get(
                "TaskName",
                ""
            ),

            filename=data.get(
                "FileName",
                ""
            ),

            group=data.get(
                "GroupName",
                ""
            ),

            enabled=to_bool(
                data.get(
                    "EnabledEvent",
                    "0"
                )
            ),

            datetime=data.get(
                "DateTime",
                ""
            ),

            use_date=to_bool(
                data.get(
                    "UseDate",
                    "0"
                )
            ),

            every_year=to_bool(
                data.get(
                    "EveryYear",
                    "0"
                )
            ),

            use_days_of_week=to_bool(
                data.get(
                    "UseDaysOfWeek",
                    "0"
                )
            ),

            days=data.get(
                "Days",
                ""
            ),

            hours=data.get(
                "Hours",
                ""
            ),

            minutes=data.get(
                "Minutes",
                ""
            ),

            seconds=to_int(
                data.get(
                    "Seconds",
                    "0"
                )
            ),

            time_type=to_int(
                data.get(
                    "TimeType",
                    "0"
                )
            ),

            immediately=to_bool(
                data.get(
                    "Immediately",
                    "0"
                )
            ),

            repeat=to_int(
                data.get(
                    "Repeat",
                    "0"
                )
            ),

            repeat_period=to_int(
                data.get(
                    "RepeatPeriod",
                    "0"
                )
            ),

            repeat_count=to_int(
                data.get(
                    "RepeatCount",
                    "0"
                )
            ),

            repeat_limit=to_int(
                data.get(
                    "RepeatLimit",
                    "0"
                )
            ),

            back_color=data.get(
                "BackColor",
                ""
            ),

            font_color=data.get(
                "FontColor",
                ""
            ),

            priority=to_int(
                data.get(
                    "Priority",
                    "0"
                )
            ),

            description=data.get(
                "Description",
                ""
            ),

            raw_data=dict(data)
        )

    # =================================================
    # Load Events
    # =================================================

    def load_events(self) -> List[Event]:

        if not self.filename:
            raise ValueError(
                "No Admin.sdl path configured."
            )

        if not os.path.exists(self.filename):
            raise FileNotFoundError(
                self.filename
            )

        parsed_events = parse_sdl_events(
            self.filename
        )

        events: List[Event] = []

        for data in parsed_events:

            event = self._build_event(
                data
            )

            events.append(event)

        return events
