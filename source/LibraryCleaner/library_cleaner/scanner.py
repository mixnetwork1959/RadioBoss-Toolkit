from __future__ import annotations

from .database import Database, DatabaseError
from .models import LibraryResult, OrphanedTrack, ScanResult


def scan_libraries(database: Database) -> ScanResult:
    """Find library rows whose track_id no longer exists in tracks2.

    This function is read-only. It does not update the database or filesystem.
    """
    for required in ("libraries", "tracks2"):
        if not database.table_exists(required):
            raise DatabaseError(f"Required RadioBOSS table is missing: {required}")

    tracks_count = int(database.fetchall("SELECT COUNT(*) FROM tracks2")[0][0])
    libraries = database.fetchall("SELECT id, name FROM libraries ORDER BY name")
    results: list[LibraryResult] = []

    for library_id, library_name in libraries:
        library_id = int(library_id)
        table_name = f"library_{library_id}"
        if not database.table_exists(table_name):
            raise DatabaseError(
                f"Library '{library_name}' references missing table {table_name}"
            )

        table = database.quote(table_name)
        total = int(database.fetchall(f"SELECT COUNT(*) FROM {table}")[0][0])
        rows = database.fetchall(
            f"SELECT l.id, l.track_id, COALESCE(l.fn, '') "
            f"FROM {table} AS l "
            "LEFT JOIN tracks2 AS t ON t.track_id = l.track_id "
            "WHERE l.track_id IS NOT NULL AND t.track_id IS NULL "
            "ORDER BY l.id"
        )
        orphaned = [
            OrphanedTrack(
                library_id=library_id,
                library_name=str(library_name),
                row_id=int(row_id),
                track_id=int(track_id),
                filename=str(filename),
            )
            for row_id, track_id, filename in rows
        ]
        results.append(
            LibraryResult(
                library_id=library_id,
                library_name=str(library_name).strip(),
                table_name=table_name,
                total_entries=total,
                orphaned=orphaned,
            )
        )

    return ScanResult(tracks_count=tracks_count, libraries=results)
