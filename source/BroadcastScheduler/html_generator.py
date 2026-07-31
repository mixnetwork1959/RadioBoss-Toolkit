# ==========================================
# Broadcast Scheduler
# Version 3.3.0
# html_generator.py
# ==========================================

from __future__ import annotations

import json
import shutil
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Iterable

from config import load_settings
from database import Database
from scheduler_controller import SchedulerController
from public_calendar_config import PublicCalendarConfig
from public_calendar_engine import PublicCalendarEngine


# =====================================================
# Constants
# =====================================================

PROJECT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = PROJECT_DIR / "templates"
OUTPUT_DIR = PROJECT_DIR / "output"

HTML_TEMPLATE = TEMPLATE_DIR / "calendar.html"
CSS_TEMPLATE = TEMPLATE_DIR / "calendar.css"
JS_TEMPLATE = TEMPLATE_DIR / "calendar.js"

OUTPUT_HTML = OUTPUT_DIR / "public_schedule.html"
OUTPUT_CSS = OUTPUT_DIR / "public_schedule.css"
OUTPUT_JS = OUTPUT_DIR / "public_schedule.js"
OUTPUT_JSON = OUTPUT_DIR / "public_schedule.json"


# =====================================================
# Helpers
# =====================================================

def _read_text(filename: Path) -> str:
    if not filename.exists():
        raise FileNotFoundError(filename)

    return filename.read_text(
        encoding="utf-8"
    )


def _write_text(
    filename: Path,
    content: str
) -> None:
    filename.write_text(
        content,
        encoding="utf-8"
    )


def _serialize_blocks(
    blocks: Iterable
) -> list[dict]:

    rows = []

    for block in blocks:

        rows.append(
            {
                "event_id": block.event_id,
                "title": block.public_name,
                "description": block.description,
                "color": block.color,
                "start": block.start.isoformat(),
                "end": block.end.isoformat(),
                "day": block.start.strftime("%A"),
                "date": block.start.strftime("%Y-%m-%d"),
                "start_time": block.start.strftime("%H:%M"),
                "end_time": block.end.strftime("%H:%M")
            }
        )

    return rows


def _week_label(blocks: list) -> str:

    if not blocks:
        return "No programs selected"

    start = min(block.start for block in blocks)
    end = max(block.end for block in blocks)

    return (
        f"{start.strftime('%b %-d')} – "
        f"{end.strftime('%b %-d, %Y')}"
    )


def _safe_week_label(blocks: list) -> str:
    """
    Windows unterstützt %-d nicht zuverlässig.
    """

    if not blocks:
        return "No programs selected"

    start = min(block.start for block in blocks)
    end = max(block.end for block in blocks)

    return (
        f"{start.strftime('%b')} {start.day} – "
        f"{end.strftime('%b')} {end.day}, {end.year}"
    )


# =====================================================
# Generator
# =====================================================

class PublicCalendarHTMLGenerator:

    def __init__(
        self,
        station_name: str = "Radio Schedule",
        station_tagline: str = "",
        config_filename: str = "public_calendar.json"
    ):

        self.station_name = station_name
        self.station_tagline = station_tagline
        self.config_filename = config_filename

    def generate(
        self,
        open_browser: bool = True
    ) -> Path:

        settings = load_settings()

        database = Database(
            settings
        )

        events = database.load_events()

        controller = SchedulerController(
            events
        )

        runtimes = controller.refresh()

        public_config = PublicCalendarConfig(
            self.config_filename
        )

        public_config.load()

        engine = PublicCalendarEngine()

        blocks = engine.detect(
            runtimes,
            public_config
        )

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        html = _read_text(
            HTML_TEMPLATE
        )

        html = html.replace(
            "{{STATION_NAME}}",
            self.station_name
        )

        html = html.replace(
            "{{STATION_TAGLINE}}",
            self.station_tagline
        )

        html = html.replace(
            "{{WEEK_LABEL}}",
            _safe_week_label(blocks)
        )

        _write_text(
            OUTPUT_HTML,
            html
        )

        shutil.copyfile(
            CSS_TEMPLATE,
            OUTPUT_CSS
        )

        shutil.copyfile(
            JS_TEMPLATE,
            OUTPUT_JS
        )

        payload = {
            "generated_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "station_name": self.station_name,
            "station_tagline": self.station_tagline,
            "week_label": _safe_week_label(blocks),
            "programs": _serialize_blocks(
                blocks
            )
        }

        _write_text(
            OUTPUT_JSON,
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2
            )
        )

        if open_browser:
            webbrowser.open(
                OUTPUT_HTML.resolve().as_uri()
            )

        return OUTPUT_HTML


# =====================================================
# Command Line Start
# =====================================================

def main():

    generator = PublicCalendarHTMLGenerator(
        station_name="Radio Albena",
        station_tagline=(
            "The Sound of the Black Sea Coast"
        )
    )

    output_file = generator.generate(
        open_browser=True
    )

    print()
    print("=" * 60)
    print("Public Calendar Website generated")
    print("=" * 60)
    print(f"HTML: {output_file}")
    print(f"JSON: {OUTPUT_JSON}")
    print(f"CSS:  {OUTPUT_CSS}")
    print(f"JS:   {OUTPUT_JS}")
    print("=" * 60)


if __name__ == "__main__":
    main()
