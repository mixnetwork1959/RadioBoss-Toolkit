from dataclasses import dataclass, field


@dataclass(frozen=True)
class OrphanedTrack:
    library_id: int
    library_name: str
    row_id: int
    track_id: int
    filename: str


@dataclass
class LibraryResult:
    library_id: int
    library_name: str
    table_name: str
    total_entries: int = 0
    orphaned: list[OrphanedTrack] = field(default_factory=list)


@dataclass
class ScanResult:
    tracks_count: int
    libraries: list[LibraryResult]

    @property
    def library_count(self) -> int:
        return len(self.libraries)

    @property
    def orphan_count(self) -> int:
        return sum(len(item.orphaned) for item in self.libraries)
