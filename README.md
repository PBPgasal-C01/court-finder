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

### 🔐 Autentikasi

- Registrasi/login (email, Google, atau social login)
- Profil user (nama, foto, preferensi main indoor/outdoor)

### 🗺️ Court Finder (Map & Filter)

- Map interaktif untuk mencari lapangan terdekat
- Filter (indoor/outdoor, gratis/berbayar, lantai beton/parquet, dll.)
- Status lapangan (aktif/ada orang main atau kosong)
- Integrasi GPS agar user bisa langsung navigasi

### 📍 Manage Court

- (Pengelola Court) Update detail lapangan: alamat, tipe, jam buka, harga sewa
- (Pengelola Court) Upload foto resmi / perbarui status (contohnya tutup sementara)
- (User) Kirim foto kondisi terbaru (masuk Media Sharing)
- Disini juga ada informasi-infromasi seperti fasilitas dan contact person dari si pengelola jika ada

### ⭐ Review & Rating

- User bisa kasih rating (bintang) dan review
- Komentar terbuka untuk pengalaman main
- Sorting court by rating/popularity views/review

### 📸 Media Sharing

- Upload foto kondisi lapangan terbaru
- Fitur "Latest Update" menampilkan unggahan terbaru per lapangan untuk cek kondisi sekarang
- Tagging lokasi supaya konten terhubung ke court tertentu

### 🏀 Game Scheduler (Cari Teman Main)

- Buat event ("Need 2 more players", "3v3 at 5 PM")
- Join game yang sudah dibuat orang lain (opsional dlu)
- Reminder & notifikasi untuk event
- Event bisa bertipe Public (muncul di list) atau Private (akses via link invite atau mungkin kayak password yang dibuat usernya sendiri gitu) (dipikirin dlu gmn caranya)
- Integrasi Google Calendar / export .ics (opsional dlu)

### 🚨 Complain & Report System

- (User) Laporkan masalah (ring rusak, lampu mati, lantai licin)
- (Pengelola Court) Respon & update status bila terkait lapangan mereka
- (Admin) Moderasi
- Status laporan: ditinjau,diproses,selesai

### ⭐ Favorit & Notifikasi

- User bisa menandai (favorite) lapangan untuk cepat diakses
- Notifikasi in-app saat:
  - Ada review baru di lapangan favorit
  - Event publik baru dibuat di lapangan favorit (opsional)
  - Ada update status (misal: lapangan ditutup sementara)

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

### 🏢 Pengelola Court

- Semua fitur registered user
- Membuat lapangan (ini harusnya bisa langsung atau gak butuh verifikasi dari admin)
- Update info lapangan: jam buka, harga sewa, fasilitas, status sementara (misal: maintenance / hujan)
- Upload media resmi (foto kondisi standar)
- Respon report yang terkait lapangan mereka (ubah status / beri catatan)
- Buat event resmi (turnamen / open court)

### ⚡ Admin

- Semua fitur registered user
- Verifikasi pembuatan lapangan oleh Pengelola Court (jika memang nanti kita buatnya harus verifikasi pembuatan lapangan)
- Moderasi konten (review, media, event) & take down jika perlu
- Override / edit data lapangan (jika ada abuse atau perbaikan data)
- Kelola seluruh report
- Manage user (Bisa hapus akun dan ban maybe)
- Analytics Dashboard: metrik seperti:
  - Jumlah user baru & aktif
  - Lapangan paling populer (berdasarkan view/ review)
  - Masalah (report) yang paling sering muncul
