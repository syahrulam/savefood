from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '12345'

# Konfigurasi Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/savefood'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Konfigurasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect ke halaman login jika belum login

# Model User
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Anda tidak memiliki akses ke halaman ini.')
            return redirect(url_for('home'))    
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin', endpoint='admin')
@admin_required
def admin():
    return render_template('admin/index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('admin/profile.html', user=current_user)


@app.route('/admin-donatur', endpoint='admin_donatur')
@admin_required
def admindonatur():
    return render_template('admin/donatur.html')

@app.route('/admin-penerima', endpoint='admin_penerima')
@admin_required
def adminpenerima():
    return render_template('admin/penerima.html')

@app.route('/admin-pengelola', endpoint='admin_pengelola')
@admin_required
def adminpengelola():
    return render_template('admin/pengelola.html')

@app.route('/data-donatur', endpoint='data_donatur')
@admin_required
def data_donatur():
    return render_template('admin/data_donatur.html')

@app.route('/data-penerima', endpoint='data_penerima')
@admin_required
def data_penerima():
    return render_template('admin/data_penerima.html')

@app.route('/data-pengelola', endpoint='data_pengelola')
@admin_required
def data_pengelola():
    return render_template('admin/data_pengelola.html')

@app.route('/kelola-akun', endpoint='kelola_akun')
@admin_required
def kelola_akun():
    return render_template('admin/kelola_akun.html')

# Routes lainnya
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/donasi')
def donasi():
    return render_template('donasi.html')

@app.route('/reduce')
def reduce():
    return render_template('reduce.html')

@app.route('/penerima')
def penerima():
    return render_template('penerima.html')

@app.route('/perorang')
def perorang():
    return render_template('perorang.html')

@app.route('/pengelola')
def pengelola():
    return render_template('pengelola.html')

@app.route('/kontak')
def kontak():
    return render_template('kontak.html')

if __name__ == '__main__':
    app.run(debug=True)
