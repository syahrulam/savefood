from extensions import db
from flask_login import UserMixin
from datetime import datetime

# Model Donasi
class Donasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_donatur = db.Column(db.String(255), nullable=False)
    nomor_telp = db.Column(db.String(20), nullable=False)
    nama_tempat = db.Column(db.String(255), nullable=False)
    jenis_makanan = db.Column(db.String(255), nullable=False)
    jumlah_porsi = db.Column(db.Integer, nullable=False)
    tanggal_kedaluwarsa = db.Column(db.Date, nullable=False)
    lokasi_donatur = db.Column(db.String(255), nullable=False)
    deskripsi_tambahan = db.Column(db.Text, nullable=True)
    tujuan = db.Column(db.String(255), nullable=False)
    file_identitas = db.Column(db.String(255), nullable=True)  # Kolom baru
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending', nullable=False)
    tanggal_donasi = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# Model Penerima
class Penerima(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_penerima = db.Column(db.String(255), nullable=False)
    kontak_penerima = db.Column(db.String(20), nullable=False)
    alamat_penerima = db.Column(db.Text, nullable=False)
    jenis_makanan_dibutuhkan = db.Column(db.String(50), nullable=False)
    jenis_penerima = db.Column(db.String(50), nullable=False)
    keterangan_penerima = db.Column(db.String(255), nullable=True)
    jumlah_kebutuhan = db.Column(db.Integer, nullable=False)
    file_identitas = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending', nullable=False)
    tanggal_pengajuan = db.Column(db.DateTime, default=datetime.utcnow)

# Model User
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)