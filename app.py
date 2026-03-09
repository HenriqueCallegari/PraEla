import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash

# Configuration
RECIPIENT_NAME = os.getenv("RECIPIENT_NAME", "Luisa Helena") 
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
_ADMIN_PASS = os.getenv("ADMIN_PASS", "ultra-secret")  # altere para algo seguro em produção

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change-me-please")
DB_PATH = os.path.join(app.root_path, "data", "messages.db")

def get_db():
    if "db" not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # admin table for hashed password (single user)
    db.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    db.commit()
    # ensure admin user exists
    cur = db.execute("SELECT id FROM admin WHERE username=?", (ADMIN_USER,)).fetchone()
    if not cur:
        p_hash = generate_password_hash(_ADMIN_PASS)
        db.execute("INSERT INTO admin (username, password_hash) VALUES (?,?)", (ADMIN_USER, p_hash))
        db.commit()

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html', name=RECIPIENT_NAME)

@app.route('/about')
def about():
    return render_template('about.html', name=RECIPIENT_NAME)

@app.route("/letters")
def letters():
    return render_template("letters.html")

@app.route("/bouquet")
def bouquet():
    return render_template("bouquet.html")

@app.route('/gallery')
def gallery():
    images = [f"img/hero0{i}.png" for i in range(1,5)]
    return render_template('gallery.html', images=images, name=RECIPIENT_NAME)

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name') or 'Anônimo'
        email = request.form.get('email') or ''
        message = request.form.get('message') or ''
        db = get_db()
        db.execute('INSERT INTO messages (name,email,message) VALUES (?,?,?)', (name,email,message))
        db.commit()
        flash('Mensagem enviada com sucesso! Obrigado ❤️', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', name=RECIPIENT_NAME)

# ADMIN
def admin_login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **k):
        if session.get('admin_logged'):
            return fn(*a, **k)
        return redirect(url_for('admin_login'))
    return wrapper

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        admin = db.execute('SELECT * FROM admin WHERE username=?', (username,)).fetchone()
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_logged'] = True
            session['admin_user'] = username
            return redirect(url_for('admin_panel'))
        flash('Usuário ou senha inválidos', 'error')
        return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged', None)
    session.pop('admin_user', None)
    return redirect(url_for('index'))

@app.route('/admin')
@admin_login_required
def admin_panel():
    db = get_db()
    rows = db.execute('SELECT * FROM messages ORDER BY created_at DESC').fetchall()
    return render_template('admin_panel.html', messages=rows)

@app.route('/admin/delete/<int:id>', methods=['POST'])
@admin_login_required
def admin_delete(id):
    db = get_db()
    db.execute('DELETE FROM messages WHERE id=?', (id,))
    db.commit()
    flash('Mensagem removida.', 'success')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    with app.app_context():
        init_db()

    app.run(debug=True)
