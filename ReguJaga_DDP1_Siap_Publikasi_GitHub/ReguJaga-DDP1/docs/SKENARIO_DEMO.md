# Skenario Demonstrasi dan Kerangka Video (target 11–12 menit)

**Gunakan data sintetik yang ada di repositori. Jangan mengklaim hasil wawancara yang belum dilakukan.**

| Waktu | Tindakan | Bukti yang perlu direkam |
|---|---|---|
| 00:00–01:15 | Latar masalah panitia, dampak ketika satu relawan batal | 2 posisi, 2 relawan dan syarat masing-masing |
| 01:15–02:15 | Jelaskan empat aturan keras dan format CSV | Tunjukkan `volunteers.csv` & `positions.csv` |
| 02:15–03:15 | Klik **Jalankan Greedy** pada kasus 01 | Hasil hanya **1/2** terisi |
| 03:15–04:30 | Klik **Optimalkan jadwal** | Hasil **2/2**, Nara di Dokumentasi dan Bima di Registrasi |
| 04:30–05:30 | Batalkan **Bima** | Hasil sah **1/2**, satu posisi kosong dengan alasan |
| 05:30–06:30 | Uji contoh 03 yang mustahil diisi semua | Tampilkan **2/4**, solusi parsial tidak dipaksakan |
| 06:30–07:45 | Atur batas node `0` | Status **BELUM TERBUKTI OPTIMAL**, meski hasil tetap valid |
| 07:45–09:15 | Terangkan diagram alur: CSV → validasi → greedy/solver → verifier → GUI/ekspor | Tunjukkan `models.py`, `rules.py`, `baseline.py`, `solver.py`, `csv_io.py`, `ui.py` |
| 09:15–10:15 | Jalankan tests dan jelaskan satu uji yang dahulu gagal (hanya jika benar ada) | Pengujian riil dan perbaikan di commit, tanpa mengarang sejarah |
| 10:15–11:15 | Ekspor CSV, jelaskan keterbatasan dan evaluasi dengan pengguna | CSV hasil, contoh hasil, potensi batas search |
| 11:15–11:45 | Buka GitHub dan jelaskan kontribusi tiap anggota | Riwayat commit sebenarnya dan link repo |

Catatan: kisaran waktu ini **target**, bukan waktu yang sudah terjadi. Bagi porsi penjelasan agar semua anggota memahami semua modul, tidak hanya bagian yang mereka edit.

## Demo algoritma dengan tangan

Jadwal greedy: `P01 → Nara`, `P02 → kosong`.

Alternatif backtracking: `P01 → Bima`, `P02 → Nara`.

Setelah Bima batal: `P01 → kosong`, `P02 → Nara` (atau pembagian sah lain dengan cakupan 1).

Kondisi batas: jika solver telah mencapai `max_nodes`, tidak boleh menyebut hasilnya optimal; sebuah pencarian pendek tidak cukup sebagai bukti global.
