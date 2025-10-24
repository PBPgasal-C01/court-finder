<div align="center">

# Court Finder

<img src="static/images/cflogo2.png" alt="Court Finder Logo" width="140" />

### _Temukan Lapangan Terdekat dengan Mudah_

</div>

---

## 📝 Deskripsi

**Court Finder** adalah aplikasi yang membantu masyarakat umum menemukan dan memantau ketersediaan fasilitas/lapangan olahraga terdekat secara real-time, menjawab kesulitan pemain kasual maupun komunitas yang sering harus datang langsung atau bergantung pada informasi tercecer di internet maupun grup chat. Selain menampilkan lokasi, aplikasi juga memberikan detail kondisi lapangan (indoor/outdoor, gratis/berbayar, material lantai,dll), bisa bermain dengan orang lain dan bisa mengecek ada event apa aja yang tersedia.Selain itu, Court Finder juga berfungsi sebagai platform bagi pemilik lapangan untuk mendaftarkan, mengelola, dan mempromosikan fasilitas olahraga mereka ke audiens yang lebih luas.

## 👥 Data Kelompok

| NPM        | Nama                     | Role              | Modul                       |
| ---------- | ------------------------ | ----------------- | --------------------------- |
| 2406495451 | Zhafira Uzma             | PJ QA (Unit test) | Complain & Report System    |
| 2406495445 | Raida Khoyyara           | PJ Figma          | Manage Court                |
| 2406408086 | Maira Azma Shaliha       | PJ Figma          | Court finder (map & filter) |
| 2406437565 | Jihan Andita Kresnaputri | PJ PM             | Game Scheduler              |
| 2406405304 | Alfino Ahmad Feriza      | PJ Developer      | Autentikasi                 |
| 2406358472 | Tristan Rasheed Satria   | PJ Developer      | Blog                        |

## 🔗 Link PWS

https://tristan-rasheed-court-finder.pbp.cs.ui.ac.id/

## 🎨 Link Design

https://www.figma.com/design/PdASDdg1WngWONePYMoFxW/Design-System?node-id=108-727&t=Isu8lalSrYHcemyl-1

## 📊 Link Sumber Dataset

https://docs.google.com/document/d/1XPr0RdUumJm2YWlrm4AMsrK8ALj-I9bUs48UgpPLh5M/edit?tab=t.0

---

# 📋 Daftar Modul

## 1. Modul Autentikasi (Alfino) 🔐

- **Fitur Autentikasi:** Registrasi/login menggunakan email, Google, atau social login , serta pengaturan profil user (nama, foto, preferensi main indoor/outdoor).

|                | Guest              | Registered User                                                   | Admin                                  |
| -------------- | ------------------ | ----------------------------------------------------------------- | -------------------------------------- |
| Peran Pengguna | Tidak dapat login. | Dapat registrasi/login, mengatur profil (nama, foto, preferensi). | Dapat mengelola akun user (hapus/ban). |

---

## 2. Modul Court Finder (Map & Filter) (Maira) 🗺️

- **Fitur Court Finder:** Menyediakan map interaktif untuk mencari lapangan, dilengkapi filter,favorit, dan sorting.

|                | Guest                                   | Registered User                                                | Admin                         |
| -------------- | --------------------------------------- | -------------------------------------------------------------- | ----------------------------- |
| Peran Pengguna | Dapat melihat map dan info dasar court. | Dapat menggunakan filter, sorting, menandai favorite lapangan. | Sama seperti Registered User. |

---

## 3. Modul Manage Court (Raida) 📍

- **CRUD Court:** Memungkinkan user (pemilik lapangan) untuk membuat, melihat, mengedit, dan menghapus (CRUD) daftar lapangan yang mereka miliki.

|                | Guest                                                                                   | Registered User                                                                           | Admin                                                                                             |
| -------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Peran Pengguna | Tidak dapat membuat/mengelola lapangan. Hanya akan melihat pesan "You have to login..." | Dapat melakukan CRUD (Create, Read, Update, Delete) penuh pada lapangan miliknya sendiri. | Admin adalah Registered User yang memiliki court. Admin hanya bisa mengelola lapangannya sendiri. |

---

## 4. Modul Blog (Tristan) 📒

- **CRUD Blog:** Pengguna dapat melihat dan menambahkan ke favourite dan juga share link dari artikel, admin dapat membuat, mengedit dan menghapus artikel.

|                | Guest                                 | Registered User                                                                                              | Admin                                                                                    |
| -------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| Peran Pengguna | Dapat melihat artikel dan share link. | Semua fitur Guest + Dapat melihat artikel favourite dan menambahkan ke my favourite artikel juga share link. | Semua fitur Registered User + Dapat membuat, mengedit dan menghapus artikel tanpa batas. |

---

## 5. Modul Game Scheduler (Cari Teman Main) (Jihan) 🏀

- **Fitur Game Scheduler:** Membuat dan bergabung dengan event, dengan opsi public/private, notifikasi, dan integrasi kalender.

|                | Guest                                                 | Registered User                                                                                                                                   | Admin                  |
| -------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| Peran Pengguna | Cuman bisa Read aja, gabisa Create, Edit, sama Delete | Bisa Create, Edit, Delete (logged user = creator, creator bisa join event bisa gak join event nya \*noted: di models ada partisipan sama creator) | sama kayak logged user |

---

## 6. Modul Complaint & Report System (Zhafira) 🚨

- **CRUD Laporan:** Fitur pelaporan masalah terkait lapangan (ring rusak, lampu mati, lantai licin), dengan status laporan yang dapat diperbarui. User bisa create, read, & delete report dan admin bisa update & read report

|                | Guest                | Registered User                         | Admin                                                                                                  |
| -------------- | -------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Peran Pengguna | Tidak dapat melapor. | Dapat melapor masalah terkait lapangan. | Dapat merespons laporan, memperbarui status (ditinjau, diproses, selesai), dan mengelola semua report. |

---

# 👤 Jenis Pengguna Website

### 🌐 Guest (tanpa login)

- Bisa lihat map dan info dasar court
- Bisa lihat rating dan review lapangan
- Bisa lihat game scheduler
- Bisa baca blog
- bisa lihat jadwal event

### 🏃‍♂️ Registered User (pemain)

- Semua fitur Guest
- Bisa buat/join game dan event
- Bisa kasih rating & review lapangan
- Bisa upload foto/video lapangan
- Bisa report masalah lapangan
- Bisa update profil dan preferensi
- Bisa menambahkan blog favorit

### ⚡ Admin

- Semua fitur Registered User
- Kelola data lapangan (buat, edit, hapus)
- Respon report (ubah status/beri catatan)
- Kelola user (hapus akun, ban)
- kelola blog (create,edit dan delete)
