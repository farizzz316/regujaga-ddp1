"""Constraint solver: MRV, backtracking, dan branch and bound.

Objektif leksikografis:
  1. Maksimalkan jumlah posisi terisi.
  2. Minimalkan maksimum tugas per relawan.
  3. Saat seri, pilih vektor ID relawan paling kecil (hasil deterministik).

Pencarian terhenti saat max_nodes dikunjungi; hasilnya valid tetapi tidak
boleh disebut optimal. Search dimulai dengan incumbent greedy yang valid.
"""
from collections.abc import Iterator

from .baseline import greedy_schedule
from .models import Position, ScheduleResult, Volunteer
from .rules import verify_schedule


def solve_schedule(volunteers: list[Volunteer], positions: list[Position],
                   max_nodes: int = 100_000) -> ScheduleResult:
    if type(max_nodes) is not int or max_nodes < 0:
        raise ValueError("max_nodes harus bilangan bulat >= 0.")
    baseline = greedy_schedule(volunteers, positions)
    pmap = {p.id: p for p in positions}
    ordered_ids = sorted(pmap)
    current: dict[str, str | None] = {}
    load = {v.id: 0 for v in volunteers}
    used_slots: dict[str, set[str]] = {v.id: set() for v in volunteers}
    best = baseline.assignment.copy()
    best_coverage = baseline.coverage
    best_max_load = baseline.max_load

    def signature(assignment: dict[str, str | None]) -> tuple:
        # Pos terisi mendahului pos kosong untuk seluruh ID Unicode.
        return tuple((assignment[pid] is None, assignment[pid]) for pid in ordered_ids)

    best_signature = signature(best)
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

    def search(remaining: tuple[str, ...], covered: int) -> Iterator[tuple[tuple[str, ...], int]]:
        nonlocal nodes, limited, best, best_coverage, best_max_load, best_signature
        if nodes >= max_nodes:
            limited = True
            return
        nodes += 1
        if covered + len(remaining) < best_coverage:
            return  # Bound: bahkan semua sisa terisi tidak akan mengalahkan incumbent.
        if not remaining:
            peak = max(load.values(), default=0)
            rank = (-covered, peak, signature(current))
            best_rank = (-best_coverage, best_max_load, best_signature)
            if rank < best_rank:
                best = current.copy()
                best_coverage = covered
                best_max_load = peak
                best_signature = rank[2]
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
            yield rest, covered + 1
            used_slots[v.id].remove(p.slot)
            load[v.id] -= 1
            del current[pid]
        current[pid] = None  # Cabang kosong selalu diperlukan untuk solusi parsial.
        yield rest, covered
        del current[pid]

    # Satu generator menyimpan pilihan dan langkah undo milik satu simpul.
    # Stack ini menjalankan DFS tanpa menambah kedalaman panggilan Python.
    stack = [search(tuple(ordered_ids), 0)]
    while stack:
        child = next(stack[-1], None)
        if limited:
            break
        if child is None:
            stack.pop()
        else:
            stack.append(search(*child))
    assert not verify_schedule(volunteers, positions, best), "Internal solver invalid."
    return ScheduleResult(
        assignment=best, coverage=best_coverage, total_positions=len(positions),
        max_load=best_max_load, nodes_explored=nodes,
        is_optimal=not limited, algorithm="Backtracking + MRV + Bound",
    )
