# Membuat Repositori Publik GitHub dan Riwayat Kontribusi Nyata

**Penting:** file ZIP yang diberikan AI adalah **kode awal**. Ia **bukan** sebuah repositori publik dan **belum** mempunyai riwayat commit anggota. Setiap anggota melakukan pekerjaan nyata lalu commit dari **akun GitHub sendiri**. Jangan membuat commit palsu, mengubah author untuk menyamar, atau mengunggah data relawan asli tanpa izin.

## Langkah 1 — Ketua membuat repositori

1. Masuk https://github.com/new.
2. `Repository name`: `regujaga-ddp1`.
3. Pilih **Public**.
4. Jangan centang *Add README* atau *Add .gitignore* bila akan mengunggah folder paket yang sudah memiliki keduanya (supaya tidak konflik).
5. Klik **Create repository**.
6. Undang seluruh anggota melalui **Settings → Collaborators → Add people**. Semua harus menerima undangan.

## Langkah 2 — Upload seluruh kode awal (oleh pemilik repo)

Ekstrak ZIP lalu buka terminal di folder `ReguJaga-DDP1`:

```bash
git init
git add .
git commit -m "chore: inisialisasi proyek ReguJaga dan prototype awal"
git branch -M main
git remote add origin https://github.com/USERNAME/regujaga-ddp1.git
git push -u origin main
```

Ganti `USERNAME` dengan username pemilik repo. Siapkan Git di https://git-scm.com/downloads . Bila belum login, GitHub meminta autentikasi melalui browser/credential manager. Jangan menempelkan token rahasia ke chat/README.

**Alternatif:** Upload file melalui **Add file → Upload files** di halaman GitHub (pilih isi folder). Namun kolaborasi harian lebih mudah menggunakan Git lokal.

## Langkah 3 — Anggota lain membuat kontribusi nyata

Masing-masing anggota melakukan clone:

```bash
git clone https://github.com/USERNAME/regujaga-ddp1.git
cd regujaga-ddp1
git switch -c fitur/NAMA-TUGAS
```

Setelah benar-benar mengerjakan dan menguji bagiannya:

```bash
python -m unittest discover -s tests -v
git add .
git commit -m "test: tambahkan kasus bentrok slot dan pembatalan"
git push -u origin fitur/NAMA-TUGAS
```

Di GitHub, buka **Pull requests → New pull request**, minta rekan mereviu, lalu merge. Jangan semua anggota mengedit file yang sama tanpa koordinasi. Pastikan `git config user.name` dan `git config user.email` sesuai identitas akun masing-masing (email dapat menggunakan noreply GitHub).

## Pembagian 4 anggota (contoh, harus dikerjakan nyata)

| Anggota | Area utama | Contoh kontribusi yang masih dibutuhkan |
|---|---|---|
| A | Data, model, aturan | Perbaiki validasi CSV, tambah kasus data nyata anonim, dokumentasikan format |
| B | Solver, evaluasi | Eksperimen batas node, jelaskan trace MRV, tambah uji oracle/benchmark |
| C | GUI dan integrasi | Penyempurnaan tampilan, uji penggunaan lintas komputer, fitur bantuan penggunaan |
| D | Verifier, kualitas | Tambah uji regresi, code review, dokumentasi risiko dan pengukuran manfaat |

**Jika tiga anggota:** A juga menangani verifier; C juga menangani ekspor. Pembagian ini adalah rekomendasi, bukan klaim bahwa pekerjaan telah dilakukan. Paket awal berisi fungsi-fungsi tersebut agar kelompok bisa memulai dari basis yang berjalan.

## Cek riwayat sebelum pengumpulan

```bash
git log --all --oneline --decorate --graph
git shortlog -sne --all
```

Periksa di GitHub halaman **Insights → Contributors** juga. Pada repositori baru, statistik contributors kadang memerlukan waktu untuk diperbarui. Yang terpenting: perubahan nyata dan commit yang dapat diperiksa.

## Syarat penyerahan

- Repo dibuat **Public** dan URL dapat dibuka tanpa login.
- README punya cara menjalankan dan menguji.
- Tidak ada data pribadi sensitif, token, `.env`, atau berkas besar tidak relevan.
- Setiap anggota tercatat berkontribusi aktif.
- Video maksimal 15 menit dan tautannya dapat dibuka.
- Deadline: **10 Desember 2026, 23.59 WIB**.
