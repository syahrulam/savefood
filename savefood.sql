-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 21, 2024 at 01:42 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `savefood`
--

-- --------------------------------------------------------

--
-- Table structure for table `penjual`
--

-- Tabel Donasi
CREATE TABLE donasi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_donatur VARCHAR(255) NOT NULL,
    nomor_telp VARCHAR(20) NOT NULL,
    nama_tempat VARCHAR(255) NOT NULL,
    jenis_makanan VARCHAR(255) NOT NULL,
    jumlah_porsi INT NOT NULL,
    tanggal_kedaluwarsa DATE NOT NULL,
    lokasi_donatur VARCHAR(255) NOT NULL,
    deskripsi_tambahan TEXT
);

-- Tabel Penerima
CREATE TABLE penerima (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_penerima VARCHAR(255) NOT NULL,
    nomor_telepon VARCHAR(20) NOT NULL,
    alamat_penerima TEXT NOT NULL,
    jenis_makanan_dibutuhkan VARCHAR(255) NOT NULL,
    jumlah_porsi_dibutuhkan INT NOT NULL,
    jenis_penerima ENUM('Perorangan', 'Yayasan', 'Lainnya') NOT NULL,
    keterangan_penerima TEXT
);

-- Tabel Daur Ulang
CREATE TABLE daur_ulang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_donatur VARCHAR(255) NOT NULL,
    nomor_telp VARCHAR(20) NOT NULL,
    nama_tempat VARCHAR(255) NOT NULL,
    jenis_makanan VARCHAR(255) NOT NULL,
    jumlah_porsi INT NOT NULL,
    tanggal_kedaluwarsa DATE NOT NULL,
    lokasi_donatur VARCHAR(255) NOT NULL,
    deskripsi_tambahan TEXT
);

-- Tabel Distribusi
CREATE TABLE distribusi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_donasi INT NOT NULL,
    id_penerima INT,
    id_daur_ulang INT,
    tanggal_distribusi DATE NOT NULL,
    status ENUM('pending', 'selesai') DEFAULT 'pending',
    FOREIGN KEY (id_donasi) REFERENCES donasi(id),
    FOREIGN KEY (id_penerima) REFERENCES penerima(id),
    FOREIGN KEY (id_daur_ulang) REFERENCES daur_ulang(id)
);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','penjual') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`, `created_at`) VALUES
(2, 'admin', 'pbkdf2:sha256:1000000$SjJT7o0f1HVakwbN$d98f0db604b0d81ee70868bd45053bd25565051e454e7918a4f772b66de90a3c', 'admin', '2024-12-21 00:24:57');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `penjual`
--
ALTER TABLE `penjual`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `penjual`
--
ALTER TABLE `penjual`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
