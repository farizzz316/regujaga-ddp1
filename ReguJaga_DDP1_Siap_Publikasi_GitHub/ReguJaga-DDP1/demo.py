"""Demo ReguJaga melalui terminal; tidak memerlukan dukungan desktop/GUI.

Contoh:
    python demo.py
    python demo.py --scenario 2
    python demo.py --cancel V02 --export output/jadwal.csv
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from regujaga.baseline import greedy_schedule
from regujaga.csv_io import export_schedule, load_project
from regujaga.rules import describe_vacancy, verify_schedule
from regujaga.solver import solve_schedule

SCENARIOS = {
    "1": "01_jebakan_greedy",
    "2": "02_jadwal_berimbang",
    "3": "03_kasus_tidak_mungkin",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Demo ReguJaga tanpa GUI")
    parser.add_argument("--scenario", choices=SCENARIOS, default="1", help="Pilih kasus contoh 1-3")
    parser.add_argument("--cancel", default="", metavar="ID", help="ID relawan yang membatalkan (contoh V02)")
    parser.add_argument("--limit", type=int, default=100_000, metavar="N", help="Batas node pencarian (default 100000)")
    parser.add_argument("--export", type=Path, metavar="PATH", help="Simpan hasil ke CSV")
    args = parser.parse_args(argv)

    path = ROOT / "data" / "demo" / SCENARIOS[args.scenario]
    volunteers, positions = load_project(path / "volunteers.csv", path / "positions.csv")
    if args.cancel:
        if args.cancel not in {v.id for v in volunteers}:
            parser.error(f"ID relawan {args.cancel!r} tidak ada pada skenario {args.scenario}")
        volunteers = [v for v in volunteers if v.id != args.cancel]
    if args.limit < 0:
        parser.error("--limit harus >= 0")

    greedy = greedy_schedule(volunteers, positions)
    solved = solve_schedule(volunteers, positions, max_nodes=args.limit)
    print(f"ReguJaga | Skenario {args.scenario}: {SCENARIOS[args.scenario]}")
    print(f"Relawan aktif: {len(volunteers)} | Kebutuhan posisi: {len(positions)}")
    if args.cancel:
        print(f"Pembatalan: {args.cancel}")
    print(f"Greedy: {greedy.coverage}/{greedy.total_positions} terisi")
    print(f"Solver: {solved.coverage}/{solved.total_positions} terisi | "
          f"beban maks: {solved.max_load} | node: {solved.nodes_explored}")
    print("Status:", "OPTIMAL (sesuai model)" if solved.is_optimal else "BELUM TERBUKTI OPTIMAL")
    print("-" * 73)
    names = {v.id: v.name for v in volunteers}
    for pos in positions:
        vid = solved.assignment[pos.id]
        assigned = f"{names[vid]} ({vid})" if vid is not None else "KOSONG"
        print(f"{pos.id:6} {pos.slot:6} {pos.role:19} => {assigned}")
        if vid is None:
            print("       Alasan:", describe_vacancy(pos, volunteers, solved.assignment, positions))
    errors = verify_schedule(volunteers, positions, solved.assignment)
    print("Verifikasi:", "LULUS (0 pelanggaran)" if not errors else "GAGAL: " + "; ".join(errors))
    if args.export:
        args.export.parent.mkdir(parents=True, exist_ok=True)
        export_schedule(args.export, positions, volunteers, solved)
        print("Ekspor CSV:", args.export)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
