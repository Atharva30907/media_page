from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'ngo_secret_key_2024'

UPLOAD_FOLDER = 'static/uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE = 'ngo_media.db'

ADMIN_USERNAME = 'Atharva'
ADMIN_PASSWORD = hashlib.sha256('3007'.encode()).hexdigest()


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS press_releases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        release_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS media_coverage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(255) NOT NULL,
        url VARCHAR(2083) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS image_gallery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path VARCHAR(2083) NOT NULL,
        description VARCHAR(255),
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_url VARCHAR(2083) NOT NULL,
        description VARCHAR(255),
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Seed sample data
    c.execute("SELECT COUNT(*) FROM press_releases")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO press_releases (title, description, release_date) VALUES (?, ?, ?)",
                  ('NGO Launches New Initiative to Support Underprivileged Children',
                   'Our NGO is excited to announce a new initiative aimed at providing education and resources to children from low-income families.',
                   '2025-01-15'))
        c.execute("INSERT INTO press_releases (title, description, release_date) VALUES (?, ?, ?)",
                  ('NGO Partners with Local Communities for Clean Water Project',
                   'In partnership with local communities, our NGO has launched a clean water initiative in rural areas.',
                   '2024-12-12'))
        c.execute("INSERT INTO media_coverage (title, url) VALUES (?, ?)",
                  ('Our NGO Featured in Global News Network', 'https://example.com/global-news'))
        c.execute("INSERT INTO media_coverage (title, url) VALUES (?, ?)",
                  ('TV Interview on Our Recent Environmental Initiative', 'https://example.com/tv-interview'))
        c.execute("INSERT INTO videos (video_url, description) VALUES (?, ?)",
                  ('https://www.youtube.com/embed/dQw4w9WgXcQ', 'NGO Impact Overview Video'))
    conn.commit()
    conn.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── PUBLIC MEDIA PAGE ────────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_db()
    press_releases = conn.execute('SELECT * FROM press_releases ORDER BY release_date DESC').fetchall()
    media_coverage = conn.execute('SELECT * FROM media_coverage ORDER BY created_at DESC').fetchall()
    images = conn.execute('SELECT * FROM image_gallery ORDER BY uploaded_at DESC').fetchall()
    videos = conn.execute('SELECT * FROM videos ORDER BY uploaded_at DESC').fetchall()
    conn.close()
    return render_template('media_page.html',
                           press_releases=press_releases,
                           media_coverage=media_coverage,
                           images=images,
                           videos=videos)


# ─── ADMIN AUTH ───────────────────────────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = hashlib.sha256(request.form.get('password', '').encode()).hexdigest()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials. Try admin / admin123', 'error')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


def require_admin():
    return session.get('admin')


# ─── ADMIN DASHBOARD ──────────────────────────────────────────────────────────

@app.route('/admin')
def admin_dashboard():
    if not require_admin():
        return redirect(url_for('admin_login'))
    conn = get_db()
    press_releases = conn.execute('SELECT * FROM press_releases ORDER BY release_date DESC').fetchall()
    media_coverage = conn.execute('SELECT * FROM media_coverage ORDER BY created_at DESC').fetchall()
    images = conn.execute('SELECT * FROM image_gallery ORDER BY uploaded_at DESC').fetchall()
    videos = conn.execute('SELECT * FROM videos ORDER BY uploaded_at DESC').fetchall()
    conn.close()
    return render_template('admin_dashboard.html',
                           press_releases=press_releases,
                           media_coverage=media_coverage,
                           images=images,
                           videos=videos)


# ─── PRESS RELEASES CRUD ──────────────────────────────────────────────────────

@app.route('/admin/press-release/add', methods=['POST'])
def add_press_release():
    if not require_admin():
        return redirect(url_for('admin_login'))
    title = request.form.get('title')
    description = request.form.get('description')
    release_date = request.form.get('release_date')
    if title and description and release_date:
        conn = get_db()
        conn.execute('INSERT INTO press_releases (title, description, release_date) VALUES (?, ?, ?)',
                     (title, description, release_date))
        conn.commit()
        conn.close()
        flash('Press release added successfully!', 'success')
    return redirect(url_for('admin_dashboard') + '#press-releases')


@app.route('/admin/press-release/edit/<int:id>', methods=['POST'])
def edit_press_release(id):
    if not require_admin():
        return redirect(url_for('admin_login'))
    title = request.form.get('title')
    description = request.form.get('description')
    release_date = request.form.get('release_date')
    conn = get_db()
    conn.execute('UPDATE press_releases SET title=?, description=?, release_date=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                 (title, description, release_date, id))
    conn.commit()
    conn.close()
    flash('Press release updated!', 'success')
    return redirect(url_for('admin_dashboard') + '#press-releases')


@app.route('/admin/press-release/delete/<int:id>')
def delete_press_release(id):
    if not require_admin():
        return redirect(url_for('admin_login'))
    conn = get_db()
    conn.execute('DELETE FROM press_releases WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Press release deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#press-releases')


# ─── MEDIA COVERAGE CRUD ──────────────────────────────────────────────────────

@app.route('/admin/media-coverage/add', methods=['POST'])
def add_media_coverage():
    if not require_admin():
        return redirect(url_for('admin_login'))
    title = request.form.get('title')
    url = request.form.get('url')
    if title and url:
        conn = get_db()
        conn.execute('INSERT INTO media_coverage (title, url) VALUES (?, ?)', (title, url))
        conn.commit()
        conn.close()
        flash('Media coverage added!', 'success')
    return redirect(url_for('admin_dashboard') + '#media-coverage')


@app.route('/admin/media-coverage/edit/<int:id>', methods=['POST'])
def edit_media_coverage(id):
    if not require_admin():
        return redirect(url_for('admin_login'))
    title = request.form.get('title')
    url = request.form.get('url')
    conn = get_db()
    conn.execute('UPDATE media_coverage SET title=?, url=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', (title, url, id))
    conn.commit()
    conn.close()
    flash('Media coverage updated!', 'success')
    return redirect(url_for('admin_dashboard') + '#media-coverage')


@app.route('/admin/media-coverage/delete/<int:id>')
def delete_media_coverage(id):
    if not require_admin():
        return redirect(url_for('admin_login'))
    conn = get_db()
    conn.execute('DELETE FROM media_coverage WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Media coverage deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#media-coverage')


# ─── IMAGE GALLERY CRUD ───────────────────────────────────────────────────────

@app.route('/admin/image/add', methods=['POST'])
def add_image():
    if not require_admin():
        return redirect(url_for('admin_login'))
    description = request.form.get('description', '')
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            conn = get_db()
            conn.execute('INSERT INTO image_gallery (image_path, description) VALUES (?, ?)',
                         (filename, description))
            conn.commit()
            conn.close()
            flash('Image uploaded successfully!', 'success')
    return redirect(url_for('admin_dashboard') + '#image-gallery')


@app.route('/admin/image/delete/<int:id>')
def delete_image(id):
    if not require_admin():
        return redirect(url_for('admin_login'))
    conn = get_db()
    row = conn.execute('SELECT image_path FROM image_gallery WHERE id=?', (id,)).fetchone()
    if row:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], row['image_path']))
        except:
            pass
        conn.execute('DELETE FROM image_gallery WHERE id=?', (id,))
        conn.commit()
    conn.close()
    flash('Image deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#image-gallery')


# ─── VIDEOS CRUD ──────────────────────────────────────────────────────────────

@app.route('/admin/video/add', methods=['POST'])
def add_video():
    if not require_admin():
        return redirect(url_for('admin_login'))
    video_url = request.form.get('video_url')
    description = request.form.get('description', '')
    if video_url:
        conn = get_db()
        conn.execute('INSERT INTO videos (video_url, description) VALUES (?, ?)', (video_url, description))
        conn.commit()
        conn.close()
        flash('Video added!', 'success')
    return redirect(url_for('admin_dashboard') + '#videos')


@app.route('/admin/video/delete/<int:id>')
def delete_video(id):
    if not require_admin():
        return redirect(url_for('admin_login'))
    conn = get_db()
    conn.execute('DELETE FROM videos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Video deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#videos')


# ─── API ENDPOINTS FOR EDIT MODALS ────────────────────────────────────────────

@app.route('/api/press-release/<int:id>')
def get_press_release(id):
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    row = conn.execute('SELECT * FROM press_releases WHERE id=?', (id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Not found'}), 404


@app.route('/api/media-coverage/<int:id>')
def get_media_coverage(id):
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    row = conn.execute('SELECT * FROM media_coverage WHERE id=?', (id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    init_db()
    app.run(debug=True, port=5000)
