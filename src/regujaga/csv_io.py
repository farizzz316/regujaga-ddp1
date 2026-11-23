"""Impor/ekspor CSV lokal berbasis modul standar csv."""
import csv
from pathlib import Path
from tempfile import NamedTemporaryFile
from .models import Position, ScheduleResult, Volunteer
from .rules import validate_data, verify_schedule

V_COLUMNS = ("id", "name", "roles", "available_slots", "max_tasks")
P_COLUMNS = ("id", "slot", "role", "location")


def _read_csv(path: str | Path, expected: tuple[str, ...]) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        try:
            if reader.fieldnames is None or set(reader.fieldnames) != set(expected) or len(reader.fieldnames) != len(expected):
                raise ValueError(f"Header {Path(path).name} wajib: {', '.join(expected)}")
            rows = []
            for line, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f"Kolom berlebih/kurang pada baris {line} di {path}.")
                rows.append({key: value.strip() for key, value in row.items()})
        except csv.Error as exc:
            raise ValueError(f"CSV {Path(path).name} tidak valid: {exc}") from exc
        return rows


def _tokens(text: str) -> frozenset[str]:
    parts = [part.strip() for part in text.split(";")]
    if any(not part for part in parts) or not parts:
        return frozenset()
    return frozenset(parts)


def load_volunteers(path: str | Path) -> list[Volunteer]:
    out = []
    for i, row in enumerate(_read_csv(path, V_COLUMNS), start=2):
        try:
            maximum = int(row["max_tasks"])
        except ValueError as exc:
            raise ValueError(f"max_tasks harus integer di baris {i}.") from exc
        out.append(Volunteer(row["id"], row["name"], _tokens(row["roles"]),
                             _tokens(row["available_slots"]), maximum))
    validate_data(out, [])
    return out


def load_positions(path: str | Path) -> list[Position]:
    rows = _read_csv(path, P_COLUMNS)
    out = [Position(row["id"], row["slot"], row["role"], row["location"]) for row in rows]
    validate_data([], out)
    return out


def load_project(volunteer_path: str | Path, position_path: str | Path) -> tuple[list[Volunteer], list[Position]]:
    volunteers, positions = load_volunteers(volunteer_path), load_positions(position_path)
    validate_data(volunteers, positions)
    return volunteers, positions


def export_schedule(path: str | Path, positions: list[Position],
                    volunteers: list[Volunteer], result: ScheduleResult) -> None:
    validate_data(volunteers, positions)
    errors = verify_schedule(volunteers, positions, result.assignment)
    if errors:
        raise ValueError("Jadwal gagal diverifikasi: " + "; ".join(errors))
    names = {v.id: v.name for v in volunteers}
    target = Path(path)
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8-sig", newline="",
                                dir=target.parent, delete=False) as handle:
            temporary = Path(handle.name)
            writer = csv.writer(handle)
            writer.writerow(("position_id", "slot", "role", "location", "volunteer_id", "volunteer_name", "status"))
            for p in positions:
                vid = result.assignment[p.id]
                writer.writerow((p.id, p.slot, p.role, p.location, vid or "",
                                 names[vid] if vid else "", "TERISI" if vid else "KOSONG"))
        temporary.replace(target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
