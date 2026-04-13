# 🌿 HopeNGO — Media Page Project

A full-stack NGO Media Page built with **Python Flask** (backend) + **HTML/CSS/JS** (frontend) + **SQLite** (database).

---

## 📁 Project Structure

```
ngo_media/
├── app.py                    ← Flask backend (all routes & DB logic)
├── requirements.txt          ← Python dependencies
├── ngo_media.db              ← SQLite database (auto-created on first run)
├── templates/
│   ├── media_page.html       ← Public-facing NGO Media Page
│   ├── admin_login.html      ← Admin login page
│   └── admin_dashboard.html  ← Admin CMS dashboard
└── static/
    └── uploads/
        └── images/           ← Uploaded gallery images stored here
```

---

## 🚀 Setup in PyCharm

### Step 1 — Open the project
Open the `ngo_media/` folder in PyCharm.

### Step 2 — Install dependencies
Open PyCharm Terminal and run:
```bash
pip install flask werkzeug
```
Or use the `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 3 — Run the app
```bash
python app.py
```

### Step 4 — Open in browser
- **Public Media Page:** http://127.0.0.1:5000/
- **Admin Login:**       http://127.0.0.1:5000/admin/login
- **Admin Dashboard:**   http://127.0.0.1:5000/admin

---

## 🔐 Admin Credentials
| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `admin123` |

---

## 📋 Features

### Public Media Page (`/`)
- ✅ Introduction / Hero section
- ✅ Press Releases with dates
- ✅ Media Coverage with external links
- ✅ Image Gallery with hover effects
- ✅ Embedded Video section
- ✅ Contact for Media section

### Admin Dashboard (`/admin`)
- ✅ Secure login with hashed password
- ✅ Stats overview (count of each content type)
- ✅ **Press Releases** — Add / Edit / Delete
- ✅ **Media Coverage** — Add / Edit / Delete
- ✅ **Image Gallery** — Upload images / Delete
- ✅ **Videos** — Add YouTube embed links / Delete
- ✅ Flash success/error messages
- ✅ Edit via modal popups (no page reload)

### Database (SQLite)
- `press_releases` table
- `media_coverage` table
- `image_gallery` table
- `videos` table

---

## 🗄️ Database Schema

| Table            | Key Columns                                      |
|------------------|--------------------------------------------------|
| press_releases   | id, title, description, release_date             |
| media_coverage   | id, title, url                                   |
| image_gallery    | id, image_path, description, uploaded_at         |
| videos           | id, video_url, description, uploaded_at          |

---

## 📝 Notes
- The SQLite database (`ngo_media.db`) is auto-created with sample data on first run.
- Uploaded images are saved in `static/uploads/images/`.
- To add YouTube videos, use the embed URL format: `https://www.youtube.com/embed/VIDEO_ID`
