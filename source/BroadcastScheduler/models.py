# ==========================================
# Broadcast Scheduler
# Version 3.0.0
# models.py
# ==========================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


# ==========================================
# Event aus der RadioBOSS Admin.sdl
# ==========================================

@dataclass
class Event:

    id: str

    # Allgemein
    name: str
    filename: str
    group: str

    enabled: bool

    # Datum / Zeit
    datetime: str
    use_date: bool
    every_year: bool

    # Wochentage / Uhrzeit
    use_days_of_week: bool
    days: str
    hours: str
    minutes: str
    seconds: int

    # Ausführungsart
    time_type: int
    immediately: bool

    # Wiederholung
    repeat: int
    repeat_period: int
    repeat_count: int
    repeat_limit: int

    # RadioBOSS-Darstellung
    back_color: str = ""
    font_color: str = ""

    # Weitere SDL-Informationen
    priority: int = 0
    description: str = ""

    # Vollständiger Originaldatensatz aus der SDL-Datei
    raw_data: Dict[str, str] = field(
        default_factory=dict
    )


# ==========================================
# Berechneter Ausführungszeitpunkt
# ==========================================

@dataclass
class RunTime:

    event: Event

    start: datetime
    end: datetime
