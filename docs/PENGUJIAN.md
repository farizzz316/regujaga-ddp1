# Pengujian ReguJaga

Dari folder yang berisi `run.py`, jalankan seluruh suite. Pada Windows, ganti `python` dengan `py` bila perlu.

```bash
python -m unittest discover -s tests -v
```

Uji integrasi membuat jendela Tk dan menekan tombol lewat `invoke()`. Uji mengganti dialog pemilih berkas dan kotak pesan agar bisa berjalan otomatis. Di desktop Linux, gunakan sesi grafis biasa. Di Linux tanpa monitor, gunakan `xvfb-run -a python -m unittest discover -s tests -v` jika Xvfb terpasang. Periksa jumlah `skipped` pada ringkasan. Tanpa Tk atau layar, tiga uji GUI akan dilewati.

## Hasil pada salinan proyek

Pada Debian Linux, 39 pengujian lulus tanpa ada yang dilewati pada Python 3.12.14 dengan Tk 9.0 dan Python 3.13.5 dengan Tk 8.6. Keduanya memakai layar virtual X11 pada mesin yang sama. Paket wheel juga berhasil dipasang di lingkungan virtual baru dan GUI memuat kedua posisi contoh.

| Percobaan dengan data demo | Greedy | Solver | Beban maksimum solver |
|---|---:|---:|---:|
| 01, semua hadir | 1/2 | 2/2 | 1 |
| 01, Bima (V02) batal | 1/2 | 1/2 | 1 |
| 02, jadwal berimbang | 6/6 | 6/6 | 2 |
| 03, kandidat terbatas | 2/4 | 2/4 | 1 |
| 01, batas node 0 | 1/2 | 1/2, belum terbukti optimal | 1 |

Untuk mereproduksi tabel dan memeriksa CSV hasil pembatalan, jalankan:

```bash
python demo.py
python demo.py --cancel V02 --export output/pembatalan.csv
python demo.py --scenario 2
python demo.py --scenario 3
python demo.py --limit 0
```

- **Algoritma.** Oracle menguji semua kombinasi penugasan pada 35 kasus kecil acak dengan seed tetap, memeriksa aturan secara mandiri, lalu membandingkan jadwal pilihan, cakupan, dan beban maksimum. Uji lain mencakup ID Unicode dan 1.100 posisi kosong dalam satu pencarian.
- **GUI.** Uji memeriksa data awal, greedy, optimasi, pembatalan, ekspor, pemulihan, batas node saat impor dan ID yang mengandung pemisah tampilan. Jika batas node salah saat pemulihan, daftar pembatalan dan hasil terakhir tetap konsisten.
- **CSV.** Uji membaca kembali berkas yang diekspor, termasuk status KOSONG dan ID serta nama relawan yang kosong. Uji kegagalan penggantian berkas memeriksa bahwa isi berkas tujuan sebelumnya tetap utuh.
- **Pemeriksaan kelompok.** Ulangi di desktop Windows anggota, gunakan dialog asli untuk memilih dan menyimpan berkas, lalu buka CSV di Excel. Catat versi Python, hasil suite, dan temuan aktual untuk laporan.
