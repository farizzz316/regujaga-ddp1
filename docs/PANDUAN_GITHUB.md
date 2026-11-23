# Bekerja di repositori ReguJaga

Repositori publik kelompok sudah tersedia di [farizzz316/regujaga-ddp1](https://github.com/farizzz316/regujaga-ddp1). Ketua mengundang anggota melalui **Settings → Collaborators**. Setiap anggota menerima undangan dengan akun sendiri.

## Mengambil kode dan mengirim perubahan

1. Clone repositori. Buka folder yang berisi `run.py`.
2. Periksa identitas Git di komputer sendiri. Mulai branch dengan nama yang sesuai pekerjaan. Contoh berikut memakai tugas pengujian dataset.

   ```bash
   git clone https://github.com/farizzz316/regujaga-ddp1.git
   cd regujaga-ddp1
   git config user.name
   git config user.email
   git switch -c uji/dataset-acara
   ```

3. Kerjakan tugas yang disepakati. Simpan hanya data anonim yang diizinkan untuk dipublikasikan.
4. Jalankan `python -m unittest discover -s tests -v`. Periksa `git diff`, tambahkan berkas yang dikerjakan dengan `git add <berkas>`, lalu periksa `git diff --cached`.
5. Buat commit dengan pesan yang menjelaskan perubahan aktual, lalu `git push -u origin HEAD`. Buka pull request dan minta rekan memeriksa perubahan serta hasil uji.
6. Tautkan PR atau commit pada catatan tugas anggota. Untuk memeriksa riwayat gunakan `git log --all --oneline --graph`.

## Penyerahan

Ketua memeriksa akses tautan repositori dan video dari jendela privat. Anggota menautkan bukti pekerjaan masing-masing. Lihat [rencana kerja](RENCANA_KERJA.md) dan [skenario video](SKENARIO_DEMO.md).

Pemilik dapat memakai `TERBITKAN_GITHUB_WINDOWS.bat` atau `bash TERBITKAN_GITHUB_MAC_LINUX.sh` dari clone ini untuk mengirim commit di `main`. Pada repositori yang sudah memiliki riwayat, skrip memeriksa branch, perubahan lokal, dan alamat tujuan push. Gunakan branch dan pull request untuk pekerjaan anggota.
