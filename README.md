<div align="center">

# Court Finder

### _Temukan Lapangan Terdekat dengan Mudah_

</div>

---

## 📝 Deskripsi

**Court Finder** adalah aplikasi yang dapat membantu pemain basket menemukan lapangan terdekat secara real-time. Selain menampilkan lokasi, aplikasi juga memberikan informasi detail tentang kondisi lapangan (indoor/outdoor, gratis/berbayar, material lantai), status aktivitas (ada orang main atau kosong), serta memungkinkan pengguna untuk menjadwalkan permainan, memberi ulasan, dan melaporkan masalah.

## 👥 Data Kelompok

| NPM        | Nama                     | Role              |
| ---------- | ------------------------ | ----------------- |
| 2406495451 | Zhafira Uzma             | PJ QA (Unit test) |
| 2406495445 | Raida Khoyyara           | PJ Figma          |
| 2406408086 | Maira Azma Shaliha       | PJ Figma          |
| 2406437565 | Jihan Andita Kresnaputri | PJ PM             |
| 2406405304 | Alfino Ahmad Feriza      | PJ Developer      |
| 2406358472 | Tristan Rasheed Satria   | PJ Developer      |

## 🔗 Link PWS

https://tristan-rasheed-court-finder.pbp.cs.ui.ac.id/

## 🎨 Link Design

https://www.figma.com/files/team/1524494717202079809/project/458189772/TK-PBP?fuid=1524494714553143203

# 📋 Daftar Modul (Draft)

## 1. Modul Autentikasi (Alfino) 🔐

- **Fitur Autentikasi:** Registrasi/login (Liat sikon) menggunakan email, Google, atau social login , serta pengaturan profil user (nama, foto, preferensi main indoor/outdoor).

|                | Guest              | Registered User                                                   | Admin                                  |
| -------------- | ------------------ | ----------------------------------------------------------------- | -------------------------------------- |
| Peran Pengguna | Tidak dapat login. | Dapat registrasi/login, mengatur profil (nama, foto, preferensi). | Dapat mengelola akun user (hapus/ban). |

---

## 2. Modul Court Finder (Map & Filter) (Maira) 🗺️

- **Fitur Court Finder:** Menyediakan map interaktif untuk mencari lapangan, dilengkapi filter, status lapangan, navigasi GPS, favorit, dan sorting.

|                | Guest                                   | Registered User                                                | Admin                         |
| -------------- | --------------------------------------- | -------------------------------------------------------------- | ----------------------------- |
| Peran Pengguna | Dapat melihat map dan info dasar court. | Dapat menggunakan filter, sorting, menandai favorite lapangan. | Sama seperti Registered User. |

---

## 3. Modul Manage Court (Raida) 📍

- **CRUD Court:** Mengelola informasi detail lapangan (alamat, tipe, jam buka, harga, foto, fasilitas, kontak), serta review dan komentar.

|                | Guest                            | Registered User                             | Admin                                                                           |
| -------------- | -------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------- |
| Peran Pengguna | Dapat melihat rating dan review. | Dapat memberi rating, review, dan komentar. | Dapat menambah, mengedit, dan menghapus data lapangan serta memperbarui status. |

---

## 4. Modul Blog (Tristan) 📒

- **CRUD Blog:** Pengguna dapat membuat, mengedit, menghapus artikel blog mereka sendiri, serta melihat dan memberi interaksi pada artikel orang lain.

|                | Guest                  | Registered User                                                                            | Admin                                      |
| -------------- | ---------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------ |
| Peran Pengguna | Dapat melihat artikel. | Dapat membuat, mengedit, dan menghapus artikel sendiri; dapat memberi like dan share link. | Dapat menghapus semua artikel tanpa batas. |

---

## 5. Modul Game Scheduler (Cari Teman Main) (Jihan) 🏀

- **Fitur Game Scheduler:** Membuat dan bergabung dengan event main basket, dengan opsi public/private, notifikasi, dan integrasi kalender.

|                | Guest                           | Registered User                                                                                                                     | Admin                         |
| -------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| Peran Pengguna | Tidak dapat membuat/join event. | Dapat membuat event, join event, memilih tipe event (public/private) (Pakai forms.py), menerima notifikasi, dan integrasi kalender. | Sama seperti Registered User. |

---

## 6. Modul Complain & Report System (Zhafira) 🚨

- **CRUD Laporan:** Fitur pelaporan masalah terkait lapangan (ring rusak, lampu mati, lantai licin), dengan status laporan yang dapat diperbarui.

|                | Guest                | Registered User                         | Admin                                                                                                  |
| -------------- | -------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Peran Pengguna | Tidak dapat melapor. | Dapat melapor masalah terkait lapangan. | Dapat merespons laporan, memperbarui status (ditinjau, diproses, selesai), dan mengelola semua report. |

---

# 👤 Jenis Pengguna Website (Tentatif)

### 🌐 Guest (tanpa login)

- Bisa lihat map dan info dasar court
- Bisa lihat rating dan review lapangan

### 🏃‍♂️ Registered User (pemain)

- Semua fitur Guest
- Bisa buat/join game dan event
- Bisa kasih rating & review lapangan
- Bisa upload foto/video lapangan
- Bisa report masalah lapangan
- Bisa update profil dan preferensi

### ⚡ Admin

- Semua fitur Registered User
- Kelola data lapangan (buat, edit, hapus)
- Respon report (ubah status/beri catatan)
- Kelola user (hapus akun, ban)

## 📊 Link Sumber Dataset

Blum ada
