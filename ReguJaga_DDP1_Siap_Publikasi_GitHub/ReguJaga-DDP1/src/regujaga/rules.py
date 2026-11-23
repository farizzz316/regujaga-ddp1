"""Aturan keras yang sama untuk greedy, backtracking, dan verifier."""
from collections import Counter
from .models import Position, Volunteer


def validate_data(volunteers: list[Volunteer], positions: list[Position]) -> None:
    """Tolak data ambigu atau tidak valid sebelum penyusunan jadwal."""
    volunteer_ids = [v.id for v in volunteers]
    position_ids = [p.id for p in positions]
    if len(set(volunteer_ids)) != len(volunteer_ids):
        raise ValueError("ID relawan duplikat.")
    if len(set(position_ids)) != len(position_ids):
        raise ValueError("ID posisi duplikat.")
    for v in volunteers:
        if not v.id or not v.name:
            raise ValueError("ID/nama relawan tidak boleh kosong.")
        if not v.roles or not v.available_slots:
            raise ValueError(f"Relawan {v.id} harus memiliki peran dan slot tersedia.")
        if type(v.max_tasks) is not int or v.max_tasks < 0:
            raise ValueError(f"Batas tugas {v.id} harus bilangan bulat >= 0.")
    for p in positions:
        if not all((p.id, p.role, p.slot, p.location)):
            raise ValueError("Semua kolom posisi harus terisi.")


def is_eligible(volunteer: Volunteer, position: Position) -> bool:
    return position.role in volunteer.roles and position.slot in volunteer.available_slots


def can_assign(volunteer: Volunteer, position: Position,
               assignment: dict[str, str | None],
               position_by_id: dict[str, Position]) -> bool:
    if not is_eligible(volunteer, position):
        return False
    existing = [position_by_id[pid] for pid, vid in assignment.items() if vid == volunteer.id]
    return len(existing) < volunteer.max_tasks and all(p.slot != position.slot for p in existing)


def verify_schedule(volunteers: list[Volunteer], positions: list[Position],
                    assignment: dict[str, str | None]) -> list[str]:
    """Kembalikan daftar kesalahan; daftar kosong = jadwal memenuhi semua aturan."""
    errors = []
    vmap = {v.id: v for v in volunteers}
    pmap = {p.id: p for p in positions}
    if set(assignment) != set(pmap):
        errors.append("Kunci hasil tidak sama dengan semua ID posisi.")
    workload = Counter()
    per_slot: set[tuple[str, str]] = set()
    for pid, vid in assignment.items():
        if pid not in pmap:
            errors.append(f"Posisi tak dikenal: {pid}")
            continue
        if vid is None:
            continue
        v = vmap.get(vid)
        p = pmap[pid]
        if v is None:
            errors.append(f"Relawan tak dikenal: {vid}")
            continue
        if not is_eligible(v, p):
            errors.append(f"{vid} tidak memenuhi peran atau waktu posisi {pid}.")
        if (vid, p.slot) in per_slot:
            errors.append(f"{vid} ditempatkan dua kali di slot {p.slot}.")
        per_slot.add((vid, p.slot))
        workload[vid] += 1
    for vid, count in workload.items():
        if count > vmap[vid].max_tasks:
            errors.append(f"{vid} memiliki {count} tugas, melebihi batas {vmap[vid].max_tasks}.")
    return errors


def describe_vacancy(position: Position, volunteers: list[Volunteer],
                     assignment: dict[str, str | None],
                     positions: list[Position]) -> str:
    """Beri alasan berdasarkan jadwal terpilih, bukan klaim bahwa semua solusi mustahil."""
    basic = [v for v in volunteers if is_eligible(v, position)]
    if not basic:
        return "Tidak ada relawan dengan peran dan ketersediaan yang cocok."
    pmap = {p.id: p for p in positions}
    possible = [v for v in basic if can_assign(v, position, assignment, pmap)]
    if possible:
        return "Ada kandidat sah; posisi dibiarkan kosong dalam hasil parsial/terbatas."
    return "Kandidat sedang mengisi slot lain atau mencapai batas tugas pada jadwal ini."
