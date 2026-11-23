# Rencana Implementasi dan Kontribusi Nyata (24 November – 10 Desember 2026)

**Status:** Repositori publik dan prototipe yang diuji tersedia. Pekerjaan teknis dibantu AI. Tugas anggota di bawah masih berupa usulan sampai ada nama penanggung jawab dan bukti pelaksanaan.

## Urutan pekerjaan

| Periode | Target | Bukti yang disimpan |
|---|---|---|
| 24 Nov | Putuskan satu acara contoh, aturan penugasan, pembagian 3–4 orang | Notulen dan persetujuan kelompok |
| 24–25 Nov | Periksa akses repo publik, undang seluruh anggota, jalankan program pada laptop masing-masing | Link GitHub, commit awal, tes lokal |
| 25–27 Nov | Temui satu koordinator acara, gali pembatalan dan aturan jadwal; isi formulir validasi | Data anonim, catatan dan persetujuan |
| 27–30 Nov | Perbaiki input/validasi, batasan, dan penyebab posisi kosong sesuai temuan | PR asli, kasus uji baru |
| 1–3 Des | Evaluasi solver vs greedy pada kasus nyata anonim dan data sintetik | Tabel perbandingan, hasil tes |
| 4–6 Des | Uji GUI pada laptop anggota; review silang per modul | Masukan anggota, perbaikan bug |
| 7–8 Des | Siapkan narasi, rekaman, dokumentasi tiap modul | Draft video, README final |
| 9 Des | Finalisasi code review, dokumentasi, unggah YouTube, cek akses publik | URL repo, video, hasil unit test |
| 10 Des sebelum 23.59 WIB | Serahkan tautan sesuai arahan dosen/asdos | Bukti submit |

## Pekerjaan konkret agar commit anggota bukan formalitas

- **Anggota 1 — Data/aturan:** Konfirmasi aturan kepada koordinator, buat pasangan CSV anonim berizin, dan catat hasil pemeriksaan input. Ubah aturan jika hasil wawancara memang mengharuskannya.
- **Anggota 2 — Algoritma:** Profiling dengan data lebih besar, pengukuran node/waktu, dan satu tes pembanding; terangkan *bound* serta MRV.
- **Anggota 3 — GUI/UX:** Uji kemudahan impor, pembatalan, ekspor; perbaiki interaksi atau pesan kesalahan; tes lintas mesin.
- **Anggota 4 — Kualitas/dokumentasi:** Tambahkan tes regresi, jalankan code review dan laporan pengujian pengguna; integrasikan demo video.

Jika **3 anggota**, gabungkan peran 4 pada anggota 1–3. Setiap orang harus bisa menjelaskan seluruh modul `models`, `rules`, `baseline`, `solver`, `csv_io`, dan `ui`.

## Checklist sebelum submit

- [ ] Ada pengguna/masalah nyata yang terkonfirmasi; jangan mengaku data demo sebagai data lapangan.
- [ ] Solusi lolos `python -m unittest discover -s tests -v` di sedikitnya dua mesin.
- [ ] Terlihat *failure case* greedy, alternatif solver, dan kegagalan solusi penuh.
- [ ] Untuk batas node kecil, label **BELUM TERBUKTI OPTIMAL** muncul.
- [ ] Repo publik, semua anggota punya commit dengan pekerjaan nyata, pull request direview.
- [ ] README relevan dengan hasil akhir; tidak memuat fitur yang belum berfungsi.
- [ ] Video <= 15 menit; URL dapat dibuka publik.
- [ ] Review dengan asdos dan catat koreksi.
