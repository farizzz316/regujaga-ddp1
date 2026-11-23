import csv
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest
from _setup import *  # noqa: F403
from regujaga.csv_io import export_schedule, load_positions, load_project, load_volunteers
from regujaga.solver import solve_schedule

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "data" / "demo" / "01_jebakan_greedy"


class CsvIOTest(unittest.TestCase):
    def test_sample_load(self):
        vs, ps = load_project(DEMO / "volunteers.csv", DEMO / "positions.csv")
        self.assertEqual((len(vs), len(ps)), (2, 2))
        self.assertEqual(vs[0].roles, frozenset({"Registrasi", "Dokumentasi"}))

    def test_export_and_read_back(self):
        vs, ps = load_project(DEMO / "volunteers.csv", DEMO / "positions.csv")
        result = solve_schedule(vs, ps)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "jadwal.csv"
            export_schedule(target, ps, vs, result)
            with open(target, encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(r["status"] == "TERISI" for r in rows))

    def test_failed_export_keeps_previous_file(self):
        vs, ps = load_project(DEMO / "volunteers.csv", DEMO / "positions.csv")
        result = solve_schedule(vs, ps)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "jadwal.csv"
            target.write_bytes(b"jadwal lama")
            with patch.object(Path, "replace", side_effect=PermissionError("terkunci")):
                with self.assertRaises(PermissionError):
                    export_schedule(target, ps, vs, result)
            self.assertEqual(target.read_bytes(), b"jadwal lama")
            self.assertEqual(list(target.parent.iterdir()), [target])

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "v.csv"
            path.write_text("id,name,roles,available_slots,max_tasks\nV,A,R,S1,1\nV,B,R,S1,1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplikat"):
                load_volunteers(path)

    def test_incorrect_header_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "positions.csv"
            path.write_text("id,slot,role\nP1,S1,R\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Header"):
                load_positions(path)

    def test_invalid_int_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "v.csv"
            path.write_text("id,name,roles,available_slots,max_tasks\nV,A,R,S1,abc\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "integer"):
                load_volunteers(path)

    def test_extra_columns_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "positions.csv"
            path.write_text("id,slot,role,location\nP1,S1,R,X,EXTRA\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "berlebih"):
                load_positions(path)

    def test_unclosed_csv_quote_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "p.csv"
            path.write_text('id,slot,role,location\nP1,S,R,"Panggung', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CSV"):
                load_positions(path)

    def test_utf8_bom(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "p.csv"
            path.write_text("\ufeffid,slot,role,location\nP1,S1,R,X\n", encoding="utf-8")
            self.assertEqual(load_positions(path)[0].id, "P1")


if __name__ == "__main__":
    unittest.main()
