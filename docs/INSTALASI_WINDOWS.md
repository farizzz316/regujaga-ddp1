# Menjalankan ReguJaga di Windows

1. Pasang Python 3.10 atau lebih baru dari [python.org](https://www.python.org/downloads/windows/). Pada installer klasik, sertakan **tcl/tk and IDLE** dan **Python Launcher**, lalu pilih **Add python.exe to PATH** jika tersedia. Buka kembali PowerShell setelah instalasi.
2. Unduh **Code → Download ZIP** dari [repositori ReguJaga](https://github.com/farizzz316/regujaga-ddp1). Pilih **Extract All**. Buka folder yang berisi `run.py`, `tests` dan `data`. Pengguna Git bisa menjalankan `git clone https://github.com/farizzz316/regujaga-ddp1.git` lalu `cd regujaga-ddp1`.
3. Di folder itu, klik kanan dan pilih **Open in Terminal**. Periksa interpreter dan buka jendela contoh Tk.

   ```powershell
   py --version
   py -m tkinter
   ```

4. Tutup jendela contoh. Klik dua kali **JALANKAN_WINDOWS.bat** atau ketik `py run.py`. Saat aplikasi terbuka, periksa tabel awal. Bima mengisi Registrasi dan Nara mengisi Dokumentasi.
5. Jalankan **UJI_WINDOWS.bat** atau `py -m unittest discover -s tests -v` di PowerShell. Periksa apakah bagian akhir menampilkan **OK** dan seluruh uji GUI dijalankan. Uji GUI memerlukan sesi desktop.
6. Untuk memeriksa hasil di Excel, batalkan V02, pilih **Ekspor CSV** dan simpan dengan nama baru. Jika Excel menampilkan satu kolom, pilih **Data → From Text/CSV**, encoding UTF-8, dengan koma sebagai pemisah. P02 seharusnya berstatus KOSONG dengan kedua kolom relawan kosong.

Jika Windows mengenali perintah `python` saja, gunakan `python` di tempat `py`. Jika modul `_tkinter` gagal dimuat, jalankan kembali pemasang Python dan tambahkan komponen Tcl/Tk. Untuk mencoba algoritma dari terminal, jalankan `py demo.py --scenario 1`. Seluruh fitur dari folder sumber memakai pustaka standar Python.
