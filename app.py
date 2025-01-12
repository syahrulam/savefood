#---------------------------------------- Configurasi Start --------------------------------
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_migrate import Migrate
from extensions import db
from models import Donasi, Penerima, User
import sys
import os
from functools import wraps

# Tambahkan path proyek secara manual
migrate = Migrate()
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


app = Flask(__name__)
app.secret_key = '12345'

# Konfigurasi Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/savefood'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

db.init_app(app)
migrate.init_app(app, db)

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'png'}

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Konfigurasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#---------------------------------------- Configurasi Done --------------------------------

#---------------------------------------- Handle Login Register Logout --------------------------------
# Route Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin'))
        flash('Login gagal. Periksa username dan password.')
    return render_template('akses/login.html')

# Route Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        # Validasi username unik
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan.')
            return redirect(url_for('register'))
        
        # Hash password menggunakan pbkdf2:sha256
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.')
        return redirect(url_for('login'))
    return render_template('akses/register.html')

def admin_required(f):
    @wraps(f)  # Memastikan nama fungsi asli tidak diubah
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Anda tidak memiliki akses ke halaman ini.')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

#---------------------------------------- Handle Login Register Logout --------------------------------

#---------------------------------------- Pengguna Page Start --------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/donasi', methods=['GET', 'POST'])
def donasi():
    if request.method == 'POST':
        try:
            # Ambil data dari form
            donatur_name = request.form['donaturName']
            phone_number = request.form['phoneNumber']
            place_name = request.form['placeName']
            food_type = request.form['foodType']
            quantity = int(request.form['quantity'])
            expiry_date = datetime.strptime(request.form['expiryDate'], '%Y-%m-%d')
            location = request.form['location']
            tujuan = request.form['tujuan']
            description = request.form.get('description', None)

            # Proses file upload
            file = request.files['file_identitas']
            if not file or not allowed_file(file.filename):
                flash('File identitas diperlukan atau format tidak didukung!', 'danger')
                return redirect(url_for('donasi'))

            # Tambahkan timestamp ke nama file
            timestamp = datetime.now().strftime('%H%M%S-%d%m%Y')  # Format: HHMMSS-DDMMYYYY
            extension = file.filename.rsplit('.', 1)[1].lower()  # Ambil ekstensi file
            filename = f"{timestamp}.{extension}"  # Gabungkan nama file dengan timestamp

            # Path relatif untuk database
            relative_file_path = f"uploads/{filename}"

            # Path absolut untuk menyimpan file
            absolute_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Pastikan folder static/uploads ada
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            file.save(absolute_file_path)  # Simpan file

            # Simpan ke database
            new_donation = Donasi(
                nama_donatur=donatur_name,
                nomor_telp=phone_number,
                nama_tempat=place_name,
                jenis_makanan=food_type,
                jumlah_porsi=quantity,
                tanggal_kedaluwarsa=expiry_date,
                lokasi_donatur=location,
                tujuan=tujuan,
                deskripsi_tambahan=description,
                file_identitas=relative_file_path,  # Simpan path relatif
                status='pending',
                tanggal_donasi=datetime.now()
            )
            db.session.add(new_donation)
            db.session.commit()

            flash('Donasi berhasil diajukan!', 'success')
            return redirect(url_for('donasi'))

        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {e}', 'danger')
            return redirect(url_for('donasi'))

    return render_template('donasi.html')

@app.route('/reduce', methods=['GET', 'POST'])
def reduce():
    if request.method == 'POST':
        try:
            # Ambil data dari form
            nama_donatur = request.form['donaturName']
            nomor_telp = request.form['phoneNumber']
            nama_tempat = request.form['placeName']
            jenis_makanan = request.form['foodType']
            jumlah_porsi = int(request.form['quantity'])
            tanggal_kedaluwarsa = datetime.strptime(request.form['expiryDate'], '%Y-%m-%d')
            lokasi_donatur = request.form['location']
            tujuan = request.form['tujuan']
            deskripsi_tambahan = request.form.get('description', None)

            # Proses file upload
            file = request.files['file_identitas']
            if not file or not allowed_file(file.filename):
                flash('File identitas diperlukan atau format tidak didukung!', 'danger')
                return redirect(url_for('reduce'))

            # Tambahkan timestamp ke nama file
            timestamp = datetime.now().strftime('%H%M%S-%d%m%Y')  # Format: HHMMSS-DDMMYYYY
            extension = file.filename.rsplit('.', 1)[1].lower()  # Ambil ekstensi file
            filename = f"{timestamp}.{extension}"  # Gabungkan nama file dengan timestamp

            # Path relatif untuk database
            relative_file_path = f"uploads/{filename}"

            # Path absolut untuk menyimpan file
            absolute_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Pastikan folder static/uploads ada
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            file.save(absolute_file_path)  # Simpan file

            # Simpan ke database
            new_reduce = Donasi(
                nama_donatur=nama_donatur,
                nomor_telp=nomor_telp,
                nama_tempat=nama_tempat,
                jenis_makanan=jenis_makanan,
                jumlah_porsi=jumlah_porsi,
                tanggal_kedaluwarsa=tanggal_kedaluwarsa,
                lokasi_donatur=lokasi_donatur,
                tujuan=tujuan,
                deskripsi_tambahan=deskripsi_tambahan,
                file_identitas=relative_file_path,  # Simpan path relatif
                status='pending',
                tanggal_donasi=datetime.now()
            )
            db.session.add(new_reduce)
            db.session.commit()

            flash('Daur ulang makanan berhasil diajukan!', 'success')
            return redirect(url_for('reduce'))

        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {e}', 'danger')
            return redirect(url_for('reduce'))

    return render_template('reduce.html')

@app.route('/penerima', methods=['GET', 'POST'])
def penerima():
    if request.method == 'POST':
        try:
            # Ambil data dari formulir
            nama_penerima = request.form['recipientName']
            kontak_penerima = request.form['recipientContact']
            alamat_penerima = request.form['recipientAddress']
            jenis_makanan = request.form['foodNeeded']
            jenis_penerima = request.form['recipientType']
            jumlah_kebutuhan = int(request.form['foodQuantity'])

            # Ambil keterangan_penerima jika ada
            keterangan_penerima = request.form.get('keterangan_penerima', None)

            # Proses file identitas
            file = request.files['file_identitas']
            if not file or not allowed_file(file.filename):
                return "File tidak valid atau format tidak didukung!", 400

            # Tambahkan timestamp ke nama file
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            extension = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{timestamp}.{extension}"
            relative_file_path = f"uploads/identitas/{filename}"
            absolute_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'identitas', filename)

            # Pastikan folder ada
            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'identitas')):
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'identitas'))

            # Simpan file
            file.save(absolute_file_path)

            # Simpan data ke database
            penerima_baru = Penerima(
                nama_penerima=nama_penerima,
                kontak_penerima=kontak_penerima,
                alamat_penerima=alamat_penerima,
                jenis_makanan_dibutuhkan=jenis_makanan,
                jenis_penerima=jenis_penerima,
                jumlah_kebutuhan=jumlah_kebutuhan,
                keterangan_penerima=keterangan_penerima,  # Menyimpan keterangan penerima
                file_identitas=relative_file_path
            )
            db.session.add(penerima_baru)
            db.session.commit()

            flash('Data penerima berhasil disimpan!', 'success')
            return redirect(url_for('penerima'))

        except Exception as e:
            db.session.rollback()
            flash(f"Terjadi kesalahan: {e}", "danger")
            return redirect(url_for('penerima'))

    return render_template('penerima.html')


#---------------------------------------- Pengguna Page End --------------------------------

#---------------------------------------- Admin Dashboard --------------------------------
# Halaman Admin Dashboard
@app.route('/admin', endpoint='admin')
@admin_required
def admin():
    return render_template('admin/index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('admin/profile.html', user=current_user)

#-------------------------------------------- Menu Permintaan ---------------------------------

# Menu Donatur - Menampilkan Data
@app.route('/admin-donatur', endpoint='admin_donatur')
@admin_required
def admindonatur():
    # Ambil data donasi dengan tujuan 'Donasikan'
    donasi_list = Donasi.query.filter_by(tujuan='Donasikan').order_by(Donasi.tanggal_donasi.desc()).all()
    return render_template('admin/donatur.html', donasi_list=donasi_list)

@app.route('/admin-donatur/approve/<int:id>', methods=['POST'])
def approve_donatur(id):
    try:
        # Ambil data donasi berdasarkan ID
        donasi = Donasi.query.get_or_404(id)
        donasi.status = 'approved'  # Perbarui status menjadi 'approved'
        db.session.commit()  # Simpan perubahan ke database
        flash('Donasi berhasil di-approve!', 'success')
    except Exception as e:
        db.session.rollback()  # Kembalikan perubahan jika ada error
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_donatur'))


@app.route('/admin-donatur/reject/<int:id>', methods=['POST'])
def reject_donatur(id):
    try:
        # Ambil data donasi berdasarkan ID
        donasi = Donasi.query.get_or_404(id)
        donasi.status = 'rejected'  # Perbarui status menjadi 'rejected'
        db.session.commit()  # Simpan perubahan ke database
        flash('Donasi berhasil di-reject!', 'success')
    except Exception as e:
        db.session.rollback()  # Kembalikan perubahan jika ada error
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_donatur'))


@app.route('/admin-pengelola', endpoint='admin_pengelola')
@admin_required
def adminpengelola():
    # Ambil data donasi dengan tujuan 'Daur Ulang'
    donasi_list = Donasi.query.filter_by(tujuan='Daur Ulang').order_by(Donasi.tanggal_donasi.desc()).all()
    return render_template('admin/pengelola.html', donasi_list=donasi_list)


@app.route('/admin-pengelola/approve/<int:id>', methods=['POST'])
def approve_pengelola(id):
    try:
        # Ambil data donasi berdasarkan ID
        donasi = Donasi.query.get_or_404(id)
        # Pastikan hanya data dengan tujuan 'Daur Ulang' yang bisa di-approve
        if donasi.tujuan == 'Daur Ulang':
            donasi.status = 'approved'  # Perbarui status menjadi 'approved'
            db.session.commit()  # Simpan perubahan ke database
            flash('Donasi berhasil di-approve!', 'success')
        else:
            flash('Hanya donasi dengan tujuan "Daur Ulang" yang dapat di-approve.', 'danger')
    except Exception as e:
        db.session.rollback()  
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_pengelola'))


@app.route('/admin-pengelola/reject/<int:id>', methods=['POST'])
def reject_pengelola(id):
    try:
        # Ambil data donasi berdasarkan ID
        donasi = Donasi.query.get_or_404(id)
        # Pastikan hanya data dengan tujuan 'Daur Ulang' yang bisa di-reject
        if donasi.tujuan == 'Daur Ulang':
            donasi.status = 'rejected'  # Perbarui status menjadi 'rejected'
            db.session.commit()  # Simpan perubahan ke database
            flash('Donasi berhasil di-reject!', 'success')
        else:
            flash('Hanya donasi dengan tujuan "Daur Ulang" yang dapat di-reject.', 'danger')
    except Exception as e:
        db.session.rollback()  # Kembalikan perubahan jika ada error
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_pengelola'))


# Menampilkan Data Penerima
@app.route('/admin-penerima', endpoint='admin_penerima')
@admin_required
def admin_penerima():
    try:
        # Ambil semua data penerima dari database
        penerima_list = Penerima.query.order_by(Penerima.tanggal_pengajuan.desc()).all()  # Urutkan berdasarkan tanggal pengajuan
        return render_template('admin/penerima.html', penerima_list=penerima_list)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin-penerima/approve/<int:id>', methods=['POST'])
@admin_required
def approve_penerima(id):
    try:
        # Ambil data penerima berdasarkan ID
        penerima = Penerima.query.get_or_404(id)
        penerima.status = 'approved'  # Ubah status menjadi 'approved'
        
        # Simpan perubahan ke database
        db.session.commit()
        
        # Tampilkan pesan sukses
        flash(f"Penerima '{penerima.nama_penerima}' berhasil di-approve!", 'success')
    except Exception as e:
        # Rollback jika terjadi error
        db.session.rollback()
        flash(f"Terjadi kesalahan saat approve: {e}", 'danger')
    return redirect(url_for('admin_penerima'))


@app.route('/admin-penerima/reject/<int:id>', methods=['POST'])
@admin_required
def reject_penerima(id):
    try:
        # Ambil data penerima berdasarkan ID
        penerima = Penerima.query.get_or_404(id)
        penerima.status = 'rejected'  # Ubah status menjadi 'rejected'
        
        # Simpan perubahan ke database
        db.session.commit()
        
        # Tampilkan pesan sukses
        flash(f"Penerima '{penerima.nama_penerima}' berhasil di-reject!", 'success')
    except Exception as e:
        # Rollback jika terjadi error
        db.session.rollback()
        flash(f"Terjadi kesalahan saat reject: {e}", 'danger')
    return redirect(url_for('admin_penerima'))

#-------------------------------------------- Menu Permintaan END ---------------------------------

#-------------------------------------------- Master Data Start ---------------------------------

@app.route('/data-donatur', endpoint='data_donatur')
@admin_required
def data_donatur():
    try:
        # Query untuk mengambil data donatur dengan status 'approved' dan menghitung total porsi berdasarkan tujuan
        donatur_data = (
            db.session.query(
                Donasi.nama_donatur,
                Donasi.nomor_telp,
                Donasi.file_identitas,
                Donasi.jenis_makanan,
                Donasi.tujuan,
                db.func.sum(Donasi.jumlah_porsi).label('total_porsi_per_jenis')
            )
            .filter(Donasi.status == 'approved')  # Hanya data dengan status 'approved'
            .group_by(
                Donasi.nama_donatur,
                Donasi.nomor_telp,
                Donasi.file_identitas,
                Donasi.jenis_makanan,
                Donasi.tujuan
            )
            .all()
        )

        # Mengelompokkan data berdasarkan nama donatur
        grouped_data = {}
        for row in donatur_data:
            nama_donatur = row.nama_donatur
            if nama_donatur not in grouped_data:
                grouped_data[nama_donatur] = {
                    "nomor_telp": row.nomor_telp,
                    "file_identitas": row.file_identitas,
                    "jenis_makanan": [],
                    "total_porsi": 0,  # Total porsi keseluruhan
                    "donasikan": 0,    # Total porsi untuk Donasikan
                    "daur_ulang": 0    # Total porsi untuk Daur Ulang
                }
            grouped_data[nama_donatur]["jenis_makanan"].append({
                "jenis": row.jenis_makanan,
                "total_porsi": row.total_porsi_per_jenis,
                "tujuan": row.tujuan
            })
            grouped_data[nama_donatur]["total_porsi"] += row.total_porsi_per_jenis
            if row.tujuan == "Donasikan":
                grouped_data[nama_donatur]["donasikan"] += row.total_porsi_per_jenis
            elif row.tujuan == "Daur Ulang":
                grouped_data[nama_donatur]["daur_ulang"] += row.total_porsi_per_jenis

        return render_template('admin/data_donatur.html', grouped_data=grouped_data)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('admin/data_donatur.html', grouped_data={})



@app.route('/data-penerima', endpoint='data_penerima')
@admin_required
def data_penerima():
    try:
        # Query untuk mengambil data penerima dengan status 'approved' dan menghitung total kebutuhan
        penerima_data = (
            db.session.query(
                Penerima.nama_penerima,
                Penerima.kontak_penerima,
                Penerima.alamat_penerima,
                Penerima.jenis_makanan_dibutuhkan,
                Penerima.jenis_penerima,
                Penerima.keterangan_penerima,
                Penerima.file_identitas,
                db.func.sum(Penerima.jumlah_kebutuhan).label('total_kebutuhan_per_jenis')
            )
            .filter(Penerima.status == 'approved')  # Hanya data dengan status 'approved'
            .group_by(
                Penerima.nama_penerima,
                Penerima.kontak_penerima,
                Penerima.alamat_penerima,
                Penerima.jenis_makanan_dibutuhkan,
                Penerima.jenis_penerima,
                Penerima.keterangan_penerima,
                Penerima.file_identitas
            )
            .all()
        )

        # Mengelompokkan data berdasarkan nama penerima
        grouped_data = {}
        for row in penerima_data:
            nama_penerima = row.nama_penerima
            if nama_penerima not in grouped_data:
                grouped_data[nama_penerima] = {
                    "kontak_penerima": row.kontak_penerima,
                    "alamat_penerima": row.alamat_penerima,
                    "jenis_penerima": row.jenis_penerima,
                    "keterangan_penerima": row.keterangan_penerima,
                    "file_identitas": row.file_identitas,
                    "jenis_makanan": [],
                    "total_kebutuhan": 0  # Total kebutuhan keseluruhan
                }
            grouped_data[nama_penerima]["jenis_makanan"].append({
                "jenis": row.jenis_makanan_dibutuhkan,
                "total_kebutuhan": row.total_kebutuhan_per_jenis
            })
            grouped_data[nama_penerima]["total_kebutuhan"] += row.total_kebutuhan_per_jenis

        return render_template('admin/data_penerima.html', grouped_data=grouped_data)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('admin/data_penerima.html', grouped_data={})


@app.route('/data-pengelola', endpoint='data_pengelola')
@admin_required
def data_pengelola():
    return render_template('admin/data_pengelola.html')


#-------------------------------------------- Master Data END ---------------------------------

@app.route('/kelola-akun', endpoint='kelola_akun')
@admin_required
def kelola_akun():
    return render_template('admin/kelola_akun.html')

#--------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Membuat tabel jika belum ada
    app.run(debug=True)