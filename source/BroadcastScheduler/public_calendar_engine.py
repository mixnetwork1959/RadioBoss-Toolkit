# ==========================================
# Broadcast Scheduler
# Version 3.1.0
# public_calendar_engine.py
# ==========================================

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Sequence


# =====================================================
# Public Program Block
# =====================================================

@dataclass
class PublicProgramBlock:

    event_id: str
    public_name: str
    description: str
    color: str

    start: datetime
    end: datetime

    occurrence_count: int

    @property
    def duration_minutes(self) -> int:

        return int(
            (self.end - self.start).total_seconds() // 60
        )


# =====================================================
# Public Calendar Engine
# =====================================================

class PublicCalendarEngine:
    """
    Erstellt öffentliche Programmblöcke ausschließlich aus Events,
    die der Administrator vorher ausgewählt hat.

    Es wird nichts anhand von Namen oder Gruppen geraten.
    """

    def __init__(
        self,
        repeat_minutes: int = 60,
        tolerance_minutes: int = 10
    ):
        self.repeat_minutes = repeat_minutes
        self.tolerance_minutes = tolerance_minutes

    # =================================================
    # Detect Selected Blocks
    # =================================================

    def detect(
        self,
        runtimes: Sequence,
        config
    ) -> List[PublicProgramBlock]:

        selected_ids = config.selected_ids()

        if not runtimes or not selected_ids:
            return []

        grouped = defaultdict(list)

        for runtime in runtimes:

            event = getattr(
                runtime,
                "event",
                None
            )

            if event is None:
                continue

            event_id = getattr(
                event,
                "id",
                ""
            )

            if event_id not in selected_ids:
                continue

            grouped[
                (
                    event_id,
                    runtime.start.date()
                )
            ].append(runtime)

        blocks: List[PublicProgramBlock] = []

        for (
            event_id,
            _date
        ), event_runtimes in grouped.items():

            event_runtimes.sort(
                key=lambda runtime: runtime.start
            )

            chains = self._build_chains(
                event_runtimes
            )

            entry = config.get_entry(
                event_id
            )

            if entry is None:
                continue

            for chain in chains:

                blocks.append(
                    self._chain_to_block(
                        chain,
                        entry
                    )
                )

        blocks.sort(
            key=lambda block: block.start
        )

        return self._merge_midnight_blocks(
            blocks
        )

    # =================================================
    # Build Hourly Chains
    # =================================================

    def _build_chains(
        self,
        runtimes: Sequence
    ) -> List[List]:

        if not runtimes:
            return []

        minimum_gap = (
            self.repeat_minutes
            - self.tolerance_minutes
        )

        maximum_gap = (
            self.repeat_minutes
            + self.tolerance_minutes
        )

        chains = []
        current = [
            runtimes[0]
        ]

        for runtime in runtimes[1:]:

            previous = current[-1]

            gap_minutes = (
                runtime.start - previous.start
            ).total_seconds() / 60

            if (
                minimum_gap
                <= gap_minutes
                <= maximum_gap
            ):
                current.append(runtime)

            else:
                chains.append(current)
                current = [runtime]

        chains.append(current)

        return chains

    # =================================================
    # Convert Chain to Block
    # =================================================

    def _chain_to_block(
        self,
        chain: Sequence,
        entry
    ) -> PublicProgramBlock:

        first = chain[0]
        last = chain[-1]

        if len(chain) >= 2:

            interval = (
                last.start - chain[-2].start
            )

        else:

            interval = timedelta(
                minutes=self.repeat_minutes
            )

        return PublicProgramBlock(
            event_id=entry.event_id,
            public_name=entry.public_name,
            description=entry.description,
            color=entry.color,
            start=first.start,
            end=last.start + interval,
            occurrence_count=len(chain)
        )

    # =================================================
    # Merge Midnight Blocks
    # =================================================

    def _merge_midnight_blocks(
        self,
        blocks: List[PublicProgramBlock]
    ) -> List[PublicProgramBlock]:
        """
        Verbindet beispielsweise:
            Monday 22:00-00:00 Night
            Tuesday 00:00-06:00 Night

        zu:
            Monday 22:00-Tuesday 06:00 Night
        """

        if not blocks:
            return []

        merged = []
        current = blocks[0]

        for block in blocks[1:]:

            same_event = (
                block.event_id
                == current.event_id
            )

            touches = (
                block.start
                == current.end
            )

            if same_event and touches:

                current = PublicProgramBlock(
                    event_id=current.event_id,
                    public_name=current.public_name,
                    description=current.description,
                    color=current.color,
                    start=current.start,
                    end=block.end,
                    occurrence_count=(
                        current.occurrence_count
                        + block.occurrence_count
                    )
                )

            else:

                merged.append(current)
                current = block

        merged.append(current)

        return merged

    # =================================================
    # Export Rows
    # =================================================

    def to_rows(
        self,
        blocks: Iterable[PublicProgramBlock]
    ) -> List[dict]:

        rows = []

        for block in blocks:

            rows.append(
                {
                    "event_id": block.event_id,
                    "public_name": block.public_name,
                    "description": block.description,
                    "color": block.color,
                    "day": block.start.strftime("%A"),
                    "date": block.start.strftime("%Y-%m-%d"),
                    "start": block.start.strftime("%H:%M"),
                    "end": block.end.strftime("%H:%M"),
                    "end_date": block.end.strftime("%Y-%m-%d"),
                    "duration_minutes": block.duration_minutes,
                    "occurrence_count": block.occurrence_count
                }
            )

        return rows
