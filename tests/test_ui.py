"""Uji tombol Tk asli. Dialog berkas dan kotak pesan diganti agar uji otomatis."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import _setup
try:
    import tkinter as tk
except ImportError:
    tk = None


@unittest.skipIf(tk is None, "Tkinter belum terpasang")
class GuiTest(unittest.TestCase):
    def setUp(self):
        from regujaga.ui import ReguJagaApp
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            if "display" in str(exc).lower():
                self.skipTest(f"Layar Tk tidak tersedia: {exc}")
            raise
        self.addCleanup(self.root.destroy)
        self.app = ReguJagaApp(self.root)
        self.root.update()

        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)

        self.buttons = {w.cget("text"): w for w in descendants(self.root)
                        if w.winfo_class() == "TButton"}
        self.assertIn("2/2", self.app.summary_var.get())

    def test_schedule_cancel_export_restore(self):
        self.assertTrue(self.buttons["Pulihkan semua"].instate(["disabled"]))
        self.buttons["Jalankan Greedy"].invoke()
        self.assertIn("1/2", self.app.summary_var.get())
        self.buttons["Optimalkan jadwal"].invoke()
        self.assertIn("2/2", self.app.summary_var.get())
        self.app.cancel_box.current(1)
        self.buttons["Batalkan kehadiran"].invoke()
        self.assertIn("1/2", self.app.summary_var.get())
        self.assertEqual(self.app.percentage_label.cget("text"), "50%")
        self.assertIn("1 relawan aktif", self.app.attendance_var.get())
        self.assertIn("vacant", self.app.tree.item(self.app.tree.get_children()[1], "tags"))
        self.assertIn("P02 [S1] kosong", self.app.log.get("1.0", "end"))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "jadwal.csv"
            with patch("tkinter.filedialog.asksaveasfilename", return_value=str(path)), \
                    patch("tkinter.messagebox.showinfo") as info:
                self.buttons["Ekspor CSV"].invoke()
                info.assert_called_once()
            with path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([(r["position_id"], r["volunteer_id"], r["volunteer_name"], r["status"])
                              for r in rows], [("P01", "V01", "Nara", "TERISI"), ("P02", "", "", "KOSONG")])
        self.buttons["Batalkan kehadiran"].invoke()
        self.assertEqual(self.app.current_result.coverage, 0)
        self.assertTrue(self.buttons["Batalkan kehadiran"].instate(["disabled"]))
        self.buttons["Pulihkan semua"].invoke()
        self.assertEqual(self.app.current_result, self.app.initial_result)

    def test_invalid_restore_keeps_cancellation_and_result(self):
        self.app.cancel_box.current(1)
        self.buttons["Batalkan kehadiran"].invoke()
        previous = self.app.current_result
        self.app.max_nodes_var.set("salah")
        with patch("tkinter.messagebox.showerror") as error:
            self.buttons["Pulihkan semua"].invoke()
            error.assert_called_once()
        self.assertEqual(self.app.cancelled, {"V02"})
        self.assertIs(self.app.current_result, previous)

    def test_import_uses_limit_and_cancel_uses_whole_id(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "relawan.csv"
            path.write_text('id,name,roles,available_slots,max_tasks\n'
                            'A - 1,"Ayu, R.",Registrasi,S1,1\n', encoding="utf-8")
            self.app.max_nodes_var.set("0")
            with patch("tkinter.filedialog.askopenfilename",
                       side_effect=[str(path), str(self.app.file_positions)]):
                self.buttons["Impor data CSV"].invoke()
            self.assertEqual(self.app.current_result.nodes_explored, 0)
            self.assertEqual(self.app.optimal_var.get(), "Belum terbukti optimal")
            self.buttons["Batalkan kehadiran"].invoke()
            self.assertEqual(self.app.cancelled, {"A - 1"})
            self.assertEqual(self.app.current_result.coverage, 0)
