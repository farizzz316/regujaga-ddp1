"""Constraint solver: MRV, recursive backtracking, dan branch and bound.

Objektif leksikografis:
  1. Maksimalkan jumlah posisi terisi.
  2. Minimalkan maksimum tugas per relawan.
  3. Saat seri, pilih vektor ID relawan paling kecil (hasil deterministik).

Pencarian terhenti saat max_nodes dikunjungi; hasilnya valid tetapi tidak
boleh disebut optimal. Search dimulai dengan incumbent greedy yang valid.
"""
from .baseline import greedy_schedule
from .models import Position, ScheduleResult, Volunteer
from .rules import can_assign, validate_data, verify_schedule


def solve_schedule(volunteers: list[Volunteer], positions: list[Position],
                   max_nodes: int = 100_000) -> ScheduleResult:
    if type(max_nodes) is not int or max_nodes < 0:
        raise ValueError("max_nodes harus bilangan bulat >= 0.")
    validate_data(volunteers, positions)
    baseline = greedy_schedule(volunteers, positions)
    pmap = {p.id: p for p in positions}
    vmap = {v.id: v for v in volunteers}
    ordered_ids = sorted(pmap)
    current: dict[str, str | None] = {}
    load = {v.id: 0 for v in volunteers}
    used_slots: dict[str, set[str]] = {v.id: set() for v in volunteers}
    best = baseline.assignment.copy()
    best_coverage = baseline.coverage
    best_max_load = baseline.max_load
    best_signature = tuple(best[pid] if best[pid] is not None else '\uffff' for pid in ordered_ids)
    nodes = 0
    limited = False

    def candidates(pos: Position) -> list[Volunteer]:
        # Filter penuh tanpa perlu membuat ulang dict penugasan.
        return sorted(
            (v for v in volunteers
             if pos.role in v.roles and pos.slot in v.available_slots
             and load[v.id] < v.max_tasks and pos.slot not in used_slots[v.id]),
            key=lambda v: (load[v.id], v.id),
        )

    def search(remaining: tuple[str, ...], covered: int) -> None:
        nonlocal nodes, limited, best, best_coverage, best_max_load, best_signature
        if nodes >= max_nodes:
            limited = True
            return
        nodes += 1
        if covered + len(remaining) < best_coverage:
            return  # Bound: bahkan semua sisa terisi tidak akan mengalahkan incumbent.
        if not remaining:
            peak = max(load.values(), default=0)
            signature = tuple(current[pid] if current[pid] is not None else '\uffff' for pid in ordered_ids)
            rank = (-covered, peak, signature)
            best_rank = (-best_coverage, best_max_load, best_signature)
            if rank < best_rank:
                best = current.copy()
                best_coverage = covered
                best_max_load = peak
                best_signature = signature
            return

        # MRV: posisi dengan kandidat tersedia paling sedikit diselesaikan dahulu.
        # Pecahkan seri menurut ID posisi agar penelusuran konsisten.
        pid = min(remaining, key=lambda x: (len(candidates(pmap[x])), x))
        p = pmap[pid]
        rest = tuple(x for x in remaining if x != pid)
        for v in candidates(p):
            current[pid] = v.id
            load[v.id] += 1
            used_slots[v.id].add(p.slot)
            search(rest, covered + 1)
            used_slots[v.id].remove(p.slot)
            load[v.id] -= 1
            del current[pid]
            if limited:
                return
        current[pid] = None  # Cabang kosong selalu diperlukan untuk solusi parsial.
        search(rest, covered)
        del current[pid]

    search(tuple(ordered_ids), 0)
    assert not verify_schedule(volunteers, positions, best), "Internal solver invalid."
    return ScheduleResult(
        assignment=best, coverage=best_coverage, total_positions=len(positions),
        max_load=best_max_load, nodes_explored=nodes,
        is_optimal=not limited, algorithm="Backtracking + MRV + Bound",
    )
