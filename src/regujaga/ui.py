"""Antarmuka desktop Tkinter/ttk untuk koordinator relawan."""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, ttk

from .baseline import greedy_schedule
from .csv_io import export_schedule, load_project
from .models import Position, ScheduleResult, Volunteer
from .rules import describe_vacancy, verify_schedule
from .solver import solve_schedule

PACKAGE = Path(__file__).resolve().parent
DEMO_ROOT = PACKAGE / "demo_data"
if not DEMO_ROOT.is_dir():
    DEMO_ROOT = PACKAGE.parents[1] / "data" / "demo"
DEMO = DEMO_ROOT / "01_jebakan_greedy"
NAVY = "#152942"
BLUE = "#1769AA"
BG = "#F7F9FB"
PANEL = "#EAF2F9"
LINE = "#CAD6E0"
MUTED = "#536578"


class ReguJagaApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("ReguJaga | Penjadwalan Relawan")
        width = min(1000, max(760, root.winfo_screenwidth() - 40))
        height = min(760, max(550, root.winfo_screenheight() - 100))
        root.geometry(f"{width}x{height}")
        root.minsize(760, 550)
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
        self.detail_var = tk.StringVar()
        self.optimal_var = tk.StringVar()
        self.load_var = tk.StringVar()
        self.attendance_var = tk.StringVar()
        self.cancel_var = tk.StringVar()
        self._configure_style()
        self._build()
        self._load(self.file_volunteers, self.file_positions)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        families = set(tkfont.families(self.root))
        self.family = next((name for name in ("Segoe UI", "Inter", "Noto Sans")
                            if name in families), tkfont.nametofont("TkDefaultFont").actual("family"))
        self.body_font = (self.family, 10)
        self.root.option_add("*TCombobox*Listbox.font", self.body_font)
        style.configure(".", font=self.body_font, foreground=NAVY, background=BG)
        style.configure("TButton", background="white", bordercolor=LINE, lightcolor="white",
                        darkcolor="white", focuscolor=BLUE, padding=(13, 6), borderwidth=1)
        style.map("TButton", background=[("pressed", "#D8E6F3"), ("active", "#EDF4FA")],
                  foreground=[("disabled", MUTED)])
        style.configure("Accent.TButton", background=BLUE, foreground="white", bordercolor=BLUE,
                        lightcolor=BLUE, darkcolor=BLUE, focuscolor="white", font=(self.family, 10, "bold"))
        style.map("Accent.TButton", background=[("pressed", "#114C80"), ("active", "#155D99")])
        style.configure("TEntry", fieldbackground="white", padding=6, bordercolor=LINE)
        style.configure("TCombobox", padding=5, arrowsize=13, bordercolor=LINE)
        style.map("TCombobox", fieldbackground=[("readonly", "white")])
        style.configure("Treeview", background="white", fieldbackground="white",
                        borderwidth=0, rowheight=tkfont.Font(font=self.body_font).metrics("linespace") + 17)
        style.configure("Treeview.Heading", background="#EBF0F5", foreground=MUTED,
                        font=(self.family, 9, "bold"), padding=(10, 7), relief="flat",
                        borderwidth=0)
        style.map("Treeview", background=[("selected", "#CFE4F6")], foreground=[("selected", NAVY)])
        style.configure("TScrollbar", arrowsize=10, background="#C3D0DA", troughcolor="#F6F8FA",
                        borderwidth=0, relief="flat")
        style.configure("Header.TButton", background=NAVY, foreground="white", bordercolor="#59718B",
                        lightcolor=NAVY, darkcolor=NAVY, focuscolor="white")
        style.map("Header.TButton", background=[("active", "#2B4968")])

    def _build(self) -> None:
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=10)
        header.pack(fill="x")
        mark = tk.Canvas(header, width=30, height=30, bg=NAVY, highlightthickness=0)
        mark.pack(side="left", padx=(0, 10))
        for x, y, color in ((3, 3, "#A8D6FF"), (16, 3, "white"),
                            (3, 16, "white"), (16, 16, "#599AD2")):
            mark.create_rectangle(x, y, x + 9, y + 9, fill=color, outline="")
        tk.Label(header, text="ReguJaga", bg=NAVY, fg="white",
                 font=(self.family, 17, "bold")).pack(side="left")
        tk.Frame(header, bg="#53687D", width=1, height=20).pack(side="left", padx=16)
        tk.Label(header, text="Penjadwalan relawan", bg=NAVY, fg="#CCD9E5",
                 font=self.body_font).pack(side="left")
        ttk.Button(header, text="Ekspor CSV", style="Header.TButton", command=self.export_csv).pack(side="right")
        ttk.Button(header, text="Impor data CSV", style="Header.TButton", command=self.import_csv).pack(side="right", padx=8)

        outer = ttk.Frame(self.root, padding=(24, 14, 24, 12))
        outer.pack(fill="both", expand=True)
        tools = ttk.Frame(outer)
        tools.pack(fill="x")
        ttk.Label(tools, text="Susun jadwal", font=(self.family, 14, "bold")).pack(side="left")
        ttk.Button(tools, text="Optimalkan jadwal", style="Accent.TButton",
                   command=self.optimize).pack(side="right")
        ttk.Button(tools, text="Jalankan Greedy", command=self.run_greedy).pack(side="right", padx=8)
        ttk.Entry(tools, textvariable=self.max_nodes_var, width=8).pack(side="right", padx=(6, 10))
        ttk.Label(tools, text="Batas node").pack(side="right")

        action = ttk.Frame(outer)
        action.pack(fill="x", pady=(9, 13))
        ttk.Label(action, text="Kehadiran relawan").pack(side="left", padx=(0, 9))
        self.cancel_box = ttk.Combobox(action, textvariable=self.cancel_var, state="readonly",
                                       font=self.body_font, width=23)
        self.cancel_box.pack(side="left")
        self.cancel_button = ttk.Button(action, text="Batalkan kehadiran", command=self.cancel_volunteer)
        self.cancel_button.pack(side="left", padx=8)
        self.restore_button = ttk.Button(action, text="Pulihkan semua", command=self.reset_cancellations)
        self.restore_button.pack(side="left")

        self._build_summary(outer)
        self._build_table(outer)
        ttk.Label(outer, text="Pemeriksaan jadwal", font=(self.family, 11, "bold")).pack(
            anchor="w", pady=(9, 4))
        notes = tk.Frame(outer, bg="white", highlightthickness=1, highlightbackground=LINE)
        notes.pack(fill="x")
        self.log = tk.Text(notes, height=2, bg="white", fg=NAVY, relief="flat", borderwidth=0,
                           font=self.body_font, wrap="word", padx=10, pady=5,
                           highlightthickness=0, state="disabled")
        scroll = ttk.Scrollbar(notes, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log.pack(side="left", fill="x", expand=True)

    def _build_summary(self, parent: ttk.Frame) -> None:
        band = tk.Frame(parent, bg=PANEL, padx=18, pady=10)
        band.pack(fill="x")
        band.columnconfigure(0, weight=1)
        band.columnconfigure(1, weight=1)
        for column, label in enumerate(("Posisi terisi", "Beban maksimum", "Status pencarian")):
            tk.Label(band, text=label, bg=PANEL, fg=MUTED, font=(self.family, 9)).grid(
                row=0, column=column, sticky="w", padx=(0, 16))
        tk.Label(band, textvariable=self.summary_var, font=(self.family, 23, "bold"),
                 bg=PANEL, fg=BLUE).grid(row=1, column=0, sticky="w")
        coverage = tk.Frame(band, bg=PANEL)
        coverage.grid(row=2, column=0, sticky="w")
        self.coverage_bar = tk.Canvas(coverage, width=84, height=5, bg="#CDDAE7",
                                      highlightthickness=0, borderwidth=0)
        self.coverage_bar.pack(side="left")
        self.coverage_fill = self.coverage_bar.create_rectangle(0, 0, 0, 5, fill=BLUE, outline="")
        self.percentage_label = tk.Label(coverage, bg=PANEL, fg=MUTED, font=(self.family, 9))
        self.percentage_label.pack(side="left", padx=(6, 0))
        tk.Label(band, textvariable=self.load_var, bg=PANEL, fg=NAVY,
                 font=(self.family, 14, "bold")).grid(row=1, column=1, sticky="w")
        tk.Label(band, textvariable=self.optimal_var, bg=PANEL, fg=NAVY,
                 font=(self.family, 12, "bold")).grid(row=1, column=2, sticky="w")
        tk.Label(band, textvariable=self.detail_var, bg=PANEL, fg=MUTED,
                 font=(self.family, 9)).grid(row=2, column=2, sticky="w")

    def _build_table(self, parent: ttk.Frame) -> None:
        title = ttk.Frame(parent)
        title.pack(fill="x", pady=(12, 6))
        ttk.Label(title, text="Penempatan relawan", font=(self.family, 14, "bold")).pack(side="left")
        ttk.Label(title, textvariable=self.attendance_var, foreground=MUTED).pack(side="right")
        frame = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground=LINE)
        frame.pack(fill="both", expand=True)
        columns = (("id", "ID posisi", 85), ("slot", "Sesi", 65), ("location", "Lokasi", 160),
                   ("role", "Peran", 145), ("volunteer", "Relawan", 150), ("status", "Status", 100))
        self.tree = ttk.Treeview(frame, columns=[c for c, _, _ in columns], show="headings", height=1)
        for key, heading, width in columns:
            self.tree.heading(key, text=heading, anchor="w")
            self.tree.column(key, width=width, minwidth=width // 2, anchor="w")
        self.tree.tag_configure("vacant", background="#FFF2DC", foreground="#77450C")
        self.tree.tag_configure("even", background="white")
        self.tree.tag_configure("odd", background="#F5F8FA")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def _load(self, volunteers_path: Path, positions_path: Path) -> None:
        try:
            volunteers, positions = load_project(volunteers_path, positions_path)
            result = solve_schedule(volunteers, positions, max_nodes=self._limit())
            self.volunteers, self.positions = volunteers, positions
            self.file_volunteers, self.file_positions = volunteers_path, positions_path
            self.cancelled.clear()
            self.initial_result = result
            self.current_result = self.initial_result
            self._refresh_cancel_options()
            self._show(self.initial_result, "Data berhasil dimuat")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Gagal memuat data", str(exc))

    def _refresh_cancel_options(self) -> None:
        labels = [f"{v.id} - {v.name}" for v in self.volunteers if v.id not in self.cancelled]
        self.cancel_box["values"] = labels
        self.cancel_var.set(labels[0] if labels else "")
        self.cancel_button.state(["!disabled" if labels else "disabled"])
        self.restore_button.state(["!disabled" if self.cancelled else "disabled"])

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
            self._reschedule(self.cancelled)
        except ValueError as exc:
            messagebox.showerror("Kesalahan", str(exc))

    def _reschedule(self, cancelled: set[str]) -> None:
        active = [v for v in self.volunteers if v.id not in cancelled]
        result = solve_schedule(active, self.positions, max_nodes=self._limit())
        if cancelled != self.cancelled:
            self.cancelled = cancelled
            self._refresh_cancel_options()
        self.current_result = result
        self._show(result, "Optimasi MRV + backtracking")

    def cancel_volunteer(self) -> None:
        index = self.cancel_box.current()
        if index < 0:
            messagebox.showinfo("Informasi", "Tidak ada relawan aktif untuk dibatalkan.")
            return
        vid = self.active_volunteers()[index].id
        try:
            self._reschedule(self.cancelled | {vid})
        except ValueError as exc:
            messagebox.showerror("Kesalahan", str(exc))

    def reset_cancellations(self) -> None:
        try:
            self._reschedule(set())
        except ValueError as exc:
            messagebox.showerror("Kesalahan", str(exc))

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
        for index, p in enumerate(self.positions):
            vid = result.assignment[p.id]
            tag = "odd" if index % 2 else "even"
            self.tree.insert("", "end", values=(p.id, p.slot, p.location, p.role,
                             names.get(vid, "—"), "Terisi" if vid else "Kosong"),
                             tags=(tag if vid else "vacant",))
        self.summary_var.set(f"{result.coverage}/{result.total_positions}")
        self.coverage_bar.coords(self.coverage_fill, 0, 0, round(84 * result.percentage / 100), 5)
        self.percentage_label.configure(text=f"{result.percentage:.0f}%")
        self.load_var.set(f"{result.max_load} tugas")
        self.optimal_var.set("Terbukti optimal" if result.is_optimal else "Belum terbukti optimal")
        self.detail_var.set(f"{result.algorithm} · {result.nodes_explored} node")
        active = self.active_volunteers()
        attendance = f"{len(active)} relawan aktif · {len(self.cancelled)} batal"
        if self.cancelled and self.initial_result is not None:
            change = result.coverage - self.initial_result.coverage
            attendance += f" · {change:+d} posisi dari awal"
        self.attendance_var.set(attendance)
        errors = verify_schedule(active, self.positions, result.assignment)
        messages = [context + ". " + ("Semua aturan terpenuhi." if not errors else "; ".join(errors))]
        for p in self.positions:
            if result.assignment[p.id] is None:
                messages.append(f"{p.id} [{p.slot}] kosong: {describe_vacancy(p, active, result.assignment, self.positions)}")
        if not result.is_optimal and result.algorithm != "Greedy (baseline)":
            messages.append("PERINGATAN: batas node tercapai; pencarian belum selesai.")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("end", "\n".join(messages))
        self.log.configure(state="disabled")
