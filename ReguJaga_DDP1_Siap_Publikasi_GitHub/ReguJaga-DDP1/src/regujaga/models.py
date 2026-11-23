"""Model domain immutable ReguJaga: relawan, posisi tugas, dan hasil pencarian."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Volunteer:
    id: str
    name: str
    roles: frozenset[str]
    available_slots: frozenset[str]
    max_tasks: int


@dataclass(frozen=True)
class Position:
    id: str
    slot: str
    role: str
    location: str


@dataclass(frozen=True)
class ScheduleResult:
    # Assignment lengkap: semua position ID harus ada, None berarti belum terisi.
    assignment: dict[str, str | None]
    coverage: int
    total_positions: int
    max_load: int
    nodes_explored: int
    is_optimal: bool
    algorithm: str

    @property
    def percentage(self) -> float:
        if self.total_positions == 0:
            return 100.0
        return self.coverage * 100.0 / self.total_positions
