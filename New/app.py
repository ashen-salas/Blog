from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_super_secreta'

# Configuración rutas absolutas
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = os.path.join(basedir, 'database.db')

# Función para validar extensiones
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['password_hash'])
    return None

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Rutas principales
@app.route('/')
def index():
    conn = get_db_connection()
    articles = conn.execute('SELECT * FROM articles ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', articles=articles)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['password_hash'])
            login_user(user_obj)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db_connection()
    articles = conn.execute('SELECT * FROM articles ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', articles=articles)

# Crear artículo con subida de imagen
@app.route('/admin/create', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files.get('image_file')
        image_url = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"Imagen guardada en: {filepath}")
            image_url = f'/static/uploads/{filename}'

        if not title or not content:
            flash('El título y contenido son obligatorios', 'warning')
            return redirect(url_for('create_article'))

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO articles (title, content, created_at, image_url) VALUES (?, ?, ?, ?)',
            (title, content, datetime.now().isoformat(), image_url)
        )
        conn.commit()
        conn.close()
        flash('Artículo creado con éxito', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('create_edit_article.html', article=None)

# Editar artículo
@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    conn = get_db_connection()
    article = conn.execute('SELECT * FROM articles WHERE id = ?', (id,)).fetchone()

    if not article:
        flash('Artículo no encontrado', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files.get('image_file')

        image_url = article['image_url']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"Imagen guardada en: {filepath}")
            image_url = f'/static/uploads/{filename}'

        if not title or not content:
            flash('El título y contenido son obligatorios', 'warning')
            return redirect(url_for('edit_article', id=id))

        conn.execute(
            'UPDATE articles SET title = ?, content = ?, image_url = ? WHERE id = ?',
            (title, content, image_url, id)
        )
        conn.commit()
        conn.close()
        flash('Artículo actualizado con éxito', 'success')
        return redirect(url_for('admin_dashboard'))

    conn.close()
    return render_template('create_edit_article.html', article=article)

# Eliminar artículo
@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def delete_article(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM articles WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Artículo eliminado', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
