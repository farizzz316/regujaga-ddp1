"""Antarmuka desktop Tkinter/ttk untuk koordinator relawan."""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .baseline import greedy_schedule
from .csv_io import export_schedule, load_project
from .models import Position, ScheduleResult, Volunteer
from .rules import describe_vacancy, verify_schedule
from .solver import solve_schedule

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "data" / "demo" / "01_jebakan_greedy"
NAVY = "#152942"
BLUE = "#1769AA"
BG = "#F4F7FB"
MUTED = "#536578"


class ReguJagaApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("ReguJaga | Penjadwalan Relawan")
        root.geometry("1040x800")
        root.minsize(850, 700)
        root.configure(bg=BG)
        self.volunteers: list[Volunteer] = []
        self.positions: list[Position] = []
        self.cancelled: set[str] = set()
        self.current_result: ScheduleResult | None = None
        self.initial_result: ScheduleResult | None = None
        self.file_volunteers = DEMO / "volunteers.csv"
        self.file_positions = DEMO / "positions.csv"
        self.max_nodes_var = tk.StringVar(value="100000")
        self.summary_var = tk.StringVar(value="Muat data untuk memulai")
        self.detail_var = tk.StringVar(value="Data contoh menggunakan nama fiktif.")
        self.cancel_var = tk.StringVar()
        self._configure_style()
        self._build()
        self._load(self.file_volunteers, self.file_positions)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=NAVY, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=NAVY, font=("Segoe UI", 23, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Card.TFrame", background="white")
        style.configure("Card.TLabel", background="white", foreground=NAVY, font=("Segoe UI", 10))
        style.configure("Accent.TButton", padding=(12, 9), font=("Segoe UI", 10, "bold"),
                        background=BLUE, foreground="white")
        style.map("Accent.TButton", background=[("active", "#125283")])
        style.configure("TButton", padding=(10, 8), font=("Segoe UI", 9))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=30,
                        background="white", fieldbackground="white", foreground=NAVY)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=7)
        style.map("Treeview", background=[("selected", "#D9ECFA")], foreground=[("selected", NAVY)])

    def _build(self) -> None:
        outer = ttk.Frame(self.root, padding=22)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="ReguJaga", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Jadwalkan relawan, kelola pembatalan, dan periksa cakupan tiap pos.",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 12))

        toolbar = ttk.Frame(outer)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(toolbar, text="Impor data CSV", command=self.import_csv).pack(side="left", padx=(0, 7))
        ttk.Button(toolbar, text="Jalankan Greedy", command=self.run_greedy).pack(side="left", padx=(0, 7))
        ttk.Button(toolbar, text="Optimalkan jadwal", style="Accent.TButton",
                   command=self.optimize).pack(side="left", padx=(0, 7))
        ttk.Button(toolbar, text="Ekspor CSV", command=self.export_csv).pack(side="left", padx=(0, 7))
        ttk.Label(toolbar, text="Batas node:").pack(side="left", padx=(10, 4))
        ttk.Entry(toolbar, textvariable=self.max_nodes_var, width=9).pack(side="left")

        action = ttk.Frame(outer)
        action.pack(fill="x", pady=(3, 10))
        ttk.Label(action, text="Pembatalan relawan:").pack(side="left", padx=(0, 8))
        self.cancel_box = ttk.Combobox(action, textvariable=self.cancel_var, state="readonly", width=32)
        self.cancel_box.pack(side="left", padx=(0, 7))
        ttk.Button(action, text="Batalkan kehadiran", command=self.cancel_volunteer).pack(side="left", padx=(0, 7))
        ttk.Button(action, text="Pulihkan semua", command=self.reset_cancellations).pack(side="left")

        summary = ttk.Frame(outer, style="Card.TFrame", padding=15)
        summary.pack(fill="x", pady=(0, 12))
        ttk.Label(summary, textvariable=self.summary_var, style="Card.TLabel",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(summary, textvariable=self.detail_var, style="Card.TLabel",
                  wraplength=940).pack(anchor="w", pady=(4, 0))

        frame = ttk.Frame(outer)
        frame.pack(fill="both", expand=True)
        columns = ("id", "slot", "location", "role", "volunteer", "status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=7)
        headers = {"id": "ID Posisi", "slot": "Sesi", "location": "Lokasi", "role": "Peran", "volunteer": "Relawan", "status": "Status"}
        widths = {"id": 100, "slot": 100, "location": 190, "role": 160, "volunteer": 200, "status": 100}
        for c in columns:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c], minwidth=80, stretch=True)
        self.tree.tag_configure("vacant", background="#FFF0E9", foreground="#9A3623")
        self.tree.tag_configure("filled", background="#F7FBFF")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        ttk.Label(outer, text="Validasi dan penjelasan pos kosong", font=("Segoe UI", 10, "bold"))\
            .pack(anchor="w", pady=(12, 4))
        self.log = tk.Text(outer, height=5, bg="white", fg=NAVY, relief="flat",
                           font=("Consolas", 10), wrap="word", padx=12, pady=8)
        self.log.pack(fill="x")
        self.log.configure(state="disabled")

    def _load(self, volunteers_path: Path, positions_path: Path) -> None:
        try:
            volunteers, positions = load_project(volunteers_path, positions_path)
            self.volunteers, self.positions = volunteers, positions
            self.file_volunteers, self.file_positions = volunteers_path, positions_path
            self.cancelled.clear()
            self.initial_result = solve_schedule(self.volunteers, self.positions)
            self.current_result = self.initial_result
            self._refresh_cancel_options()
            self._show(self.initial_result, "Data berhasil dimuat")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Gagal memuat data", str(exc))

    def _refresh_cancel_options(self) -> None:
        labels = [f"{v.id} - {v.name}" for v in self.volunteers if v.id not in self.cancelled]
        self.cancel_box["values"] = labels
        self.cancel_var.set(labels[0] if labels else "")

    def active_volunteers(self) -> list[Volunteer]:
        return [v for v in self.volunteers if v.id not in self.cancelled]

    def import_csv(self) -> None:
        v = filedialog.askopenfilename(title="Pilih volunteers.csv", filetypes=[("CSV", "*.csv")])
        if not v:
            return
        p = filedialog.askopenfilename(title="Pilih positions.csv", filetypes=[("CSV", "*.csv")])
        if p:
            self._load(Path(v), Path(p))

    def _limit(self) -> int:
        try:
            value = int(self.max_nodes_var.get().strip())
            if value < 0:
                raise ValueError
            return value
        except ValueError as exc:
            raise ValueError("Batas node harus integer >= 0.") from exc

    def run_greedy(self) -> None:
        try:
            result = greedy_schedule(self.active_volunteers(), self.positions)
            self.current_result = result
            self._show(result, "Greedy sesuai urutan masukan CSV")
        except ValueError as exc:
            messagebox.showerror("Kesalahan", str(exc))

    def optimize(self) -> None:
        try:
            result = solve_schedule(self.active_volunteers(), self.positions, max_nodes=self._limit())
            self.current_result = result
            self._show(result, "Optimasi MRV + backtracking")
        except ValueError as exc:
            messagebox.showerror("Kesalahan", str(exc))

    def cancel_volunteer(self) -> None:
        choice = self.cancel_var.get()
        if not choice:
            messagebox.showinfo("Informasi", "Tidak ada relawan aktif untuk dibatalkan.")
            return
        try:
            self._limit()
        except ValueError as exc:
            messagebox.showerror("Kesalahan", str(exc))
            return
        vid = choice.split(" - ", 1)[0]
        self.cancelled.add(vid)
        self._refresh_cancel_options()
        self.optimize()

    def reset_cancellations(self) -> None:
        self.cancelled.clear()
        self._refresh_cancel_options()
        self.optimize()

    def export_csv(self) -> None:
        if self.current_result is None:
            return
        path = filedialog.asksaveasfilename(title="Simpan jadwal", defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")], initialfile="jadwal_regujaga.csv")
        if not path:
            return
        try:
            export_schedule(path, self.positions, self.active_volunteers(), self.current_result)
            messagebox.showinfo("Ekspor selesai", f"Jadwal tersimpan di:\n{path}")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Ekspor gagal", str(exc))

    def _show(self, result: ScheduleResult, context: str) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        names = {v.id: v.name for v in self.volunteers}
        for p in self.positions:
            vid = result.assignment[p.id]
            self.tree.insert("", "end", values=(p.id, p.slot, p.location, p.role,
                             names.get(vid, "-- Belum terisi --"), "TERISI" if vid else "KOSONG"),
                             tags=("filled" if vid else "vacant",))
        delta = ""
        if self.initial_result is not None and self.cancelled:
            delta = f" | Perubahan dari jadwal awal: {result.coverage - self.initial_result.coverage:+d} posisi"
        label = "OPTIMAL TERBUKTI (untuk model ini)" if result.is_optimal else "HASIL VALID, BELUM TERBUKTI OPTIMAL"
        self.summary_var.set(
            f"{result.coverage}/{result.total_positions} posisi terisi ({result.percentage:.0f}%)"
            f"  |  Beban maksimum {result.max_load} tugas  |  {label}"
        )
        self.detail_var.set(
            f"{context} | {result.algorithm} | {result.nodes_explored} node ditelusuri"
            f" | {len(self.cancelled)} pembatalan{delta}"
        )
        errors = verify_schedule(self.active_volunteers(), self.positions, result.assignment)
        messages = ["Pemeriksaan aturan: " + ("LULUS (tidak ada pelanggaran)" if not errors else "; ".join(errors))]
        for p in self.positions:
            if result.assignment[p.id] is None:
                messages.append(f"{p.id} [{p.slot}] kosong: {describe_vacancy(p, self.active_volunteers(), result.assignment, self.positions)}")
        if not result.is_optimal and result.algorithm != "Greedy (baseline)":
            messages.append("PERINGATAN: batas node tercapai; pencarian belum selesai.")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("end", "\n".join(messages))
        self.log.configure(state="disabled")
