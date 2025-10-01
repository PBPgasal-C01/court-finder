<div align="center">

# Court Finder

### _Temukan Lapangan Terdekat dengan Mudah_

</div>

---

## 📝 Deskripsi

**Court Finder** adalah aplikasi yang dapat membantu pemain basket menemukan lapangan terdekat secara real-time. Selain menampilkan lokasi, aplikasi juga memberikan informasi detail tentang kondisi lapangan (indoor/outdoor, gratis/berbayar, material lantai), status aktivitas (ada orang main atau kosong), serta memungkinkan pengguna untuk menjadwalkan permainan, memberi ulasan, dan melaporkan masalah.

## 👥 Data Kelompok

| NPM        | Nama                     |
| ---------- | ------------------------ |
| 2406495451 | Zhafira Uzma             |
| 2406495445 | Raida Khoyyara           |
| 2406408086 | Maira Azma Shaliha       |
| 2406437565 | Jihan Andita Kresnaputri |
| 2406405304 | Alfino Ahmad Feriza      |
| 2406358472 | Tristan Rasheed Satria   |

## 🔗 Link PWS

Blum ada

## 🎨 Link Design

https://www.figma.com/files/team/1524494717202079809/project/458189772/TK-PBP?fuid=1524494714553143203

## 📋 Daftar Modul (Draft)

### 🔐 Autentikasi - Alfino

Registrasi/login (email, Google, atau social login)
Profil user (nama, foto, preferensi main indoor/outdoor)

### 🗺️ Court Finder (Map & Filter) - Maira

Map interaktif untuk mencari lapangan terdekat
Filter (indoor/outdoor, gratis/berbayar, lantai beton/parquet, dll.)
Status lapangan (aktif/ada orang main atau kosong)
Integrasi GPS agar user bisa langsung navigasi
User bisa menandai (favorite) lapangan untuk cepat diakses (opsional)
Sorting court by rating/popularity views/review

### 📍 Manage Court - Raida

(Admin) Update detail lapangan: alamat, tipe, jam buka, harga sewa
(Admin) Upload foto resmi / perbarui status (contohnya tutup sementara)
Disini juga ada informasi-infromasi seperti fasilitas dan contact person dari si pengelola jika ada
User bisa kasih rating (bintang) dan review
Komentar terbuka untuk pengalaman main

### 📒 Blog - Tristan

(user pembuat) membuat , mengedit dan mengedit artikel blognya sendiri yang bisa dibaca
(user pelihat) bisa di like dan dilihat viewsnya dan creator
(user) bisa menshare pake link
(admin) delete artikel semuanya tanpa terbatas

### 🏀 Game Scheduler (Cari Teman Main) - Jihan

Buat event ("Need 2 more players", "3v3 at 5 PM")
Join game yang sudah dibuat orang lain (opsional dlu)
Reminder & notifikasi untuk event
Event bisa bertipe Public (muncul di list) atau Private (akses via link invite atau mungkin kayak password yang dibuat usernya sendiri gitu) (ada forms.py kalau private)
Integrasi Google Calendar / export .ics

### 🚨 Complain & Report System - Zhafira

(User) Laporkan masalah (ring rusak, lampu mati, lantai licin)
(admin) Respon & update status bila terkait lapangan mereka
Status laporan: ditinjau,diproses,selesai

## 📊 Link Sumber Dataset

Blum ada

## 👤 Jenis Pengguna Website (Tentatif)

### 🌐 Guest (tanpa login)

- Bisa lihat map dan info dasar court
- Bisa lihat rating dan review lapangan

### 🏃‍♂️ Registered User (pemain)

- Semua fitur guest
- Bisa buat/join game dan event
- Bisa kasih rating & review lapangan
- Bisa upload foto/video lapangan
- Bisa report masalah lapangan
- Bisa update profil dan preferensi (Maybe?)

### ⚡ Admin

- Semua fitur registered user
- Admin dari manage court (bisa buat edit dana delete)
- Respon report yang terkait lapangan mereka (ubah status / beri catatan)
- Kelola dan respons seluruh report
- Manage user (Bisa hapus akun dan ban maybe)

## Role

### PJ Figma

- Raida

- Maira

### QA (Unit test)

- Zhafira

### PM

- Jihan

### PJ Developer

- alfino
- Tristan
