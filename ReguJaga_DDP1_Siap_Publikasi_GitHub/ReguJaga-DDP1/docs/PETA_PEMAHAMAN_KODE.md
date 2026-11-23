# Peta Pemahaman Kode untuk Seluruh Anggota

Bacalah berurutan. Materi wajib DDP1: variabel, pilihan, perulangan, fungsi, collections, berkas, exception, rekursi, OOP, GUI. Eksplorasi proyek: CSP, MRV, backtracking, branch-and-bound.

| File | Tanggung jawab | Bagian yang harus bisa dijelaskan |
|---|---|---|
| `models.py` | Kelas data domain | `@dataclass`, `Volunteer`, `Position`, `ScheduleResult`, `None` berarti kosong |
| `csv_io.py` | I/O | `csv.DictReader`, validasi header, `utf-8-sig`, `csv.writer` |
| `rules.py` | Pemeriksaan aturan | `is_eligible`, `can_assign`, `verify_schedule`, larangan dua tugas simultan |
| `baseline.py` | Metode pembanding | Greedy memakai urutan data, tidak memperbaiki keputusan awal |
| `solver.py` | Optimasi | DFS rekursif, MRV dinamis, cabang kosong, undo, batas cakupan, status limit node |
| `ui.py` | Pengalaman pengguna | Tombol, event handler, data aktif vs batal, pemanggilan solver dan verifier |
| `app.py` dan `run.py` | Startup | Memulai Tkinter dari folder proyek |
| `demo.py` | Demo tanpa jendela | `argparse`, pilihan skenario, pembatalan dan ekspor |
| `tests/` | Pembuktian perilaku | `unittest` dan oracle enumerasi exhaustive pada data kecil |

## Lima pertanyaan yang wajib bisa dijawab saat ditanya asdos

1. Mengapa metode greedy menghasilkan satu posisi kosong pada kasus 01, sedangkan backtracking mengisi dua?
2. Apa bedanya *rekursi biasa* yang dipelajari di kelas dengan pencarian CSP menggunakan MRV?
3. Kapan penugasan relawan dianggap tidak sah, dan di mana aturan itu diverifikasi?
4. Mengapa algoritma tetap dapat mengembalikan hasil saat tidak ada solusi penuh? Mengapa ketika `--limit 0` tidak boleh mengklaim optimal?
5. Bagaimana perubahan data CSV mengubah keputusan solver, dan apa asumsi slot yang tidak overlap?

## Contoh pengujian yang bisa didemokan

```powershell
python demo.py
python demo.py --scenario 3
python demo.py --cancel V02
python demo.py --limit 0
python -m unittest discover -s tests -v
```

Selalu sebutkan: jadwal yang optimal itu optimal **pada model batasan yang diterapkan**. Belum menangani durasi tak seragam, perjalanan antar-pos, dan ketentuan istirahat.
