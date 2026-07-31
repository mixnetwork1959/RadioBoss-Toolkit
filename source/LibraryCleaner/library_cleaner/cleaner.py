from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .database import Database, DatabaseError, SQLiteDatabase
from .models import ScanResult
from .scanner import scan_libraries


def default_backup_directory() -> Path:
    root = os.environ.get("LOCALAPPDATA")
    if root:
        return Path(root) / "RadioBOSS Library Cleaner" / "backups"
    return Path.home() / "RadioBOSS Library Cleaner" / "backups"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def create_backup(database: Database, result: ScanResult, directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    stamp = _timestamp()
    created: list[Path] = []

    if isinstance(database, SQLiteDatabase):
        database_copy = directory / f"tracks-before-cleanup-{stamp}.db"
        database.backup_to(database_copy)
        created.append(database_copy)

    report = directory / f"orphaned-entries-{stamp}.json"
    payload = {
        "created_at": datetime.now().astimezone().isoformat(),
        "tracks_count": result.tracks_count,
        "library_count": result.library_count,
        "orphan_count": result.orphan_count,
        "libraries": [
            {
                "library_id": item.library_id,
                "library_name": item.library_name,
                "table_name": item.table_name,
                "entries": [asdict(orphan) for orphan in item.orphaned],
            }
            for item in result.libraries
            if item.orphaned
        ],
    }
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    created.append(report)
    return created


def clean_orphaned_entries(
    database: Database,
    backup_directory: Path | None = None,
) -> tuple[ScanResult, int, list[Path]]:
    """Rescan, back up and remove only rows that are still orphaned."""
    result = scan_libraries(database)
    if result.orphan_count == 0:
        return result, 0, []

    backup_paths = create_backup(
        database, result, backup_directory or default_backup_directory()
    )
    deleted = 0
    marker = database.placeholder
    try:
        for library in result.libraries:
            table = database.quote(library.table_name)
            for orphan in library.orphaned:
                sql = (
                    f"DELETE FROM {table} WHERE id={marker} AND track_id={marker} "
                    f"AND NOT EXISTS (SELECT 1 FROM tracks2 WHERE track_id={marker})"
                )
                deleted += database.execute(
                    sql, (orphan.row_id, orphan.track_id, orphan.track_id)
                )
        database.commit()
    except Exception as exc:
        database.rollback()
        raise DatabaseError(f"Cleanup was rolled back: {exc}") from exc
    return result, deleted, backup_paths
