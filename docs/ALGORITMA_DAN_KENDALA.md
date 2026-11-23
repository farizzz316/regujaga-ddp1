# Kontrak Data, Kendala, dan Pembuktian Hasil

## 1. Definisi

- **Volunteer**: `id`, `name`, `roles` (set), `available_slots` (set), `max_tasks` (integer >= 0).
- **Position**: `id`, `slot`, `role`, `location`. Dua kebutuhan orang untuk satu pos = dua ID posisi.
- **Assignment**: mapping `position_id → volunteer_id atau None` (kosong).
- **Slot**: kategori waktu diskret non-overlap; `S1` dan `S2` diasumsikan berbeda dan tidak tumpang tindih.

## 2. Kendala keras

Untuk setiap pasangan penugasan `(posisi, relawan)`:

1. Peran posisi harus terdapat dalam `volunteer.roles`.
2. `position.slot` harus terdapat dalam `volunteer.available_slots`.
3. Satu relawan hanya boleh mengisi **satu posisi per slot**.
4. Jumlah tugas seorang relawan tidak boleh melebihi `max_tasks`.
5. Semua posisi selalu tercatat; yang tidak terisi bernilai `None`.

## 3. Objektif leksikografis

Dengan `C = jumlah posisi terisi`, `M = maksimum tugas yang dialokasikan kepada satu relawan`:

1. Maksimalkan `C`.
2. Di antara jadwal dengan `C` sama, minimalkan `M`.
3. Pecahkan seri berikutnya secara deterministik berdasarkan ID relawan pada urutan ID posisi. Pos terisi mendahului pos kosong, termasuk ketika ID berisi Unicode.

Ini **bukan** optimasi jumlah perubahan penugasan setelah pembatalan; belum menjadi fitur MVP.

## 4. Pseudocode

```text
best <- greedy(data), hasil sah awal
DFS(remaining_positions, assignment_sementara):
    if node_count mencapai batas:
        tandai hasil 'pencarian dibatasi'; kembali
    if covered + len(remaining) < best.covered:
        kembali  # tak mungkin lebih baik dari jumlah terisi
    if remaining kosong:
        evaluasi (cakupan, beban maksimum, ID)
        perbarui best bila lebih baik
        kembali
    pilih posisi MRV dengan kandidat sah paling sedikit
    untuk setiap kandidat sah, urut beban lalu ID:
        masukkan penugasan; DFS(sisa); undo
    coba posisi tanpa relawan (None); DFS(sisa); undo
kembalikan best dan apakah seluruh pencarian tuntas
```

### MRV

Pada setiap state, kandidat dihitung lagi berdasarkan **beban saat itu** dan **slot yang sudah dipakai**. Posisi paling sulit dicoba lebih awal supaya kegagalan terlihat cepat.

### Bound

Jika `covered + remaining < best_coverage`, sisa posisi bahkan bila semuanya terisi **tidak** dapat meningkatkan cakupan. Pencarian dipangkas. Bila hasil seri cakupan masih mungkin memiliki beban maksimum lebih kecil, cabang tersebut tetap diperiksa.

### Batas node

`max_nodes` dapat diubah lewat UI. `0` berarti tidak melakukan DFS dan hanya mengembalikan solusi greedy sah; pada `max_nodes` kecil hasil tetap valid tetapi **tidak optimal terbukti**. Dengan budget default 100000 node dan data 2–6 posisi, demo dapat diselesaikan cepat pada komputer biasa. Kinerja pada data besar perlu diukur ulang, tidak dijamin.

### Dari pseudocode ke Python

Pseudocode di atas menunjukkan DFS secara rekursif. Di `solver.py`, setiap simpul adalah generator. Saat generator menghasilkan cabang anak dengan `yield`, loop menaruh anak di puncak stack. Setelah anak selesai, generator induk dilanjutkan untuk melepas slot dan mengurangi beban. Dengan cara ini, jadwal panjang dapat ditelusuri tanpa terkena batas kedalaman rekursi interpreter.

Jika V adalah jumlah relawan dan P jumlah posisi, pohon memiliki paling banyak V+1 pilihan per tingkat, termasuk pilihan kosong. Jumlah daun dalam kasus terburuk mencapai (V+1)^P. MRV mengubah urutan pencarian. Bound mengurangi jumlah cabang yang perlu diperiksa. Cakupan yang masih bisa seri tetap diperiksa untuk membandingkan beban dan urutan ID.

Pembatalan menyaring relawan aktif dan menjalankan solver kembali dengan batas node pada layar. Pulihkan semua menjalankan solver atas daftar lengkap. Hasil baru, status pembatalan, dan tabel diperbarui bersama setelah penghitungan berhasil. Ekspor memeriksa seluruh penugasan terhadap relawan aktif, lalu menulis satu baris per posisi dalam urutan CSV masukan.

## 5. Mengapa greedy kalah pada kasus 01

Urutan posisi CSV: P01 Registrasi, P02 Dokumentasi, keduanya S1.

- Nara: Registrasi **atau** Dokumentasi, maksimal 1 tugas.
- Bima: hanya Registrasi, maksimal 1 tugas.
- Greedy menerima Nara lebih awal untuk P01, lalu P02 tidak memiliki kandidat → **1/2**.
- Backtracking mencoba pilihan lain: Bima untuk P01, Nara untuk P02 → **2/2**.
- Setelah Bima batal, Nara tidak bisa mengerjakan dua tugas simultan → **1/2**, sesuai aturan.

## 6. Bukti benar yang dapat direproduksi

`verify_schedule` terpisah dari implementasi solver dan mendeteksi pelanggaran keras. `tests/test_solver.py` memiliki oracle exhaustive independen yang membandingkan cakupan, beban maksimum, dan seluruh penugasan pada puluhan kasus kecil. Uji ini tidak merupakan bukti formal untuk setiap input, tetapi mengurangi risiko kesalahan implementasi dan dapat diulang.

## 7. Konsep materi vs eksplorasi

| Sudah menjadi fondasi materi DDP1 | Eksplorasi di luar materi yang dibuktikan dalam proyek |
|---|---|
| `if`, `for`, `while`, fungsi, `dict`, `set`, rekursi, class, Tkinter, CSV | Formulasi CSP penugasan; pemilihan variabel MRV dinamis; DFS backtracking dengan optimasi leksikografis; branch-and-bound berbasis batas cakupan; pembanding exhaustive independen |

**Batas klaim:** MRV, CSP, dan branch-and-bound tidak ditunjukkan sebagai teknik eksplisit dalam 19 bahan yang dikaji dalam dokumen riset. Bila asdos mengajarkannya secara lisan/di lab tambahan, sesuaikan penjelasan kebaruan.
