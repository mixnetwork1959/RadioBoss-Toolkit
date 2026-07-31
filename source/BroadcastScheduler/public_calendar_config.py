# ==========================================
# Broadcast Scheduler
# Version 3.1.0
# public_calendar_config.py
# ==========================================

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List


# =====================================================
# Public Calendar Entry
# =====================================================

@dataclass
class PublicCalendarEntry:
    """
    Öffentliche Darstellung eines ausgewählten RadioBOSS-Events.
    """

    event_id: str
    public_name: str
    description: str = ""
    color: str = "#4EA3FF"
    enabled: bool = True


# =====================================================
# Public Calendar Config
# =====================================================

class PublicCalendarConfig:
    """
    Lädt und speichert die Auswahl für den öffentlichen Kalender.

    Die Event-ID ist der stabile Schlüssel. Interne Eventnamen dürfen
    später geändert werden, ohne dass die Auswahl verloren geht.
    """

    def __init__(
        self,
        filename: str = "public_calendar.json"
    ):
        self.filename = filename
        self.entries: Dict[str, PublicCalendarEntry] = {}

    # =================================================
    # Load
    # =================================================

    def load(self) -> None:

        self.entries = {}

        if not os.path.exists(self.filename):
            return

        with open(
            self.filename,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        for item in data.get(
            "programs",
            []
        ):

            event_id = str(
                item.get(
                    "event_id",
                    ""
                )
            ).strip()

            if not event_id:
                continue

            entry = PublicCalendarEntry(
                event_id=event_id,
                public_name=str(
                    item.get(
                        "public_name",
                        ""
                    )
                ).strip(),
                description=str(
                    item.get(
                        "description",
                        ""
                    )
                ).strip(),
                color=str(
                    item.get(
                        "color",
                        "#4EA3FF"
                    )
                ).strip() or "#4EA3FF",
                enabled=bool(
                    item.get(
                        "enabled",
                        True
                    )
                )
            )

            self.entries[event_id] = entry

    # =================================================
    # Save
    # =================================================

    def save(self) -> None:

        data = {
            "version": 1,
            "programs": [
                asdict(entry)
                for entry in sorted(
                    self.entries.values(),
                    key=lambda item: item.public_name.lower()
                )
            ]
        }

        with open(
            self.filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )

    # =================================================
    # Entry Management
    # =================================================

    def set_entry(
        self,
        entry: PublicCalendarEntry
    ) -> None:

        self.entries[entry.event_id] = entry

    def remove_entry(
        self,
        event_id: str
    ) -> None:

        self.entries.pop(
            event_id,
            None
        )

    def get_entry(
        self,
        event_id: str
    ):

        return self.entries.get(
            event_id
        )

    def is_selected(
        self,
        event_id: str
    ) -> bool:

        entry = self.get_entry(
            event_id
        )

        return bool(
            entry
            and entry.enabled
        )

    def selected_ids(self) -> set:

        return {
            event_id
            for event_id, entry in self.entries.items()
            if entry.enabled
        }

    # =================================================
    # Event Suggestions
    # =================================================

    def build_event_candidates(
        self,
        events: Iterable
    ) -> List[dict]:
        """
        Liefert eine eindeutige Liste aller RadioBOSS-Events für die GUI.
        """

        candidates = []
        seen = set()

        for event in events:

            event_id = getattr(
                event,
                "id",
                ""
            )

            if not event_id or event_id in seen:
                continue

            seen.add(event_id)

            existing = self.get_entry(
                event_id
            )

            candidates.append(
                {
                    "event_id": event_id,
                    "internal_name": getattr(
                        event,
                        "name",
                        ""
                    ),
                    "group_name": getattr(
                        event,
                        "group",
                        ""
                    ),
                    "selected": bool(
                        existing
                        and existing.enabled
                    ),
                    "public_name": (
                        existing.public_name
                        if existing
                        else getattr(
                            event,
                            "name",
                            ""
                        )
                    ),
                    "description": (
                        existing.description
                        if existing
                        else ""
                    ),
                    "color": (
                        existing.color
                        if existing
                        else "#4EA3FF"
                    )
                }
            )

        candidates.sort(
            key=lambda item: (
                item["internal_name"].lower(),
                item["event_id"]
            )
        )

        return candidates
