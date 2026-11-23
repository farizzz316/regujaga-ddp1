"""Baseline: greedy sesuai urutan CSV, tanpa meninjau ulang pilihan awal."""
from .models import Position, ScheduleResult, Volunteer
from .rules import can_assign, validate_data


def greedy_schedule(volunteers: list[Volunteer], positions: list[Position]) -> ScheduleResult:
    validate_data(volunteers, positions)
    assignment: dict[str, str | None] = {}
    pmap = {p.id: p for p in positions}
    for p in positions:
        assignment[p.id] = None
        for v in volunteers:
            if can_assign(v, p, assignment, pmap):
                assignment[p.id] = v.id
                break
    counts = {v.id: sum(vid == v.id for vid in assignment.values()) for v in volunteers}
    return ScheduleResult(
        assignment=assignment, coverage=sum(vid is not None for vid in assignment.values()),
        total_positions=len(positions), max_load=max(counts.values(), default=0),
        nodes_explored=len(positions), is_optimal=False, algorithm="Greedy (baseline)",
    )
