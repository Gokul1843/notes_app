from flask import Flask, render_template, request, redirect, session
import sqlite3
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

# Load local .env
load_dotenv()

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# Cloudinary Config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Database setup
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    db = get_db()
    c = db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            url TEXT
        )
    """)
    db.commit()
    db.close()

init_db()

# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            db = get_db()
            c = db.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            db.close()
            return redirect("login.html")
        except sqlite3.IntegrityError:
            return "Username already exists"

    return render_template("signup.html")

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Admin login
        if username == "admin" and password == "admin123":
            session["user"] = "admin"
            return redirect("dashboard.html")

        # Check normal user
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        db.close()

        if user:
            session["user"] = username
            return redirect("dashboard.html")
        else:
            return "Invalid login"

    return render_template("login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("login.html")

# ---------- DASHBOARD ----------
@app.route("dashboard.html")
def dashboard():
    if "user" not in session:
        return redirect("login.html")

    db = get_db()
    c = db.cursor()
    c.execute("SELECT filename, url FROM notes")
    notes = c.fetchall()
    db.close()

    is_admin = session["user"] == "admin"
    return render_template("dashboard.html", notes=notes, is_admin=is_admin)

# ---------- UPLOAD (ADMIN ONLY) ----------
@app.route("/upload", methods=["POST"])
def upload():
    if session.get("user") != "admin":
        return "Not allowed"

    file = request.files.get("file")
    if not file:
        return "No file selected"

    try:
        result = cloudinary.uploader.upload(file)
        file_url = result.get("secure_url")
        if not file_url:
            return "Upload failed: Cloudinary did not return URL"

        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO notes (filename, url) VALUES (?, ?)", (file.filename, file_url))
        db.commit()
        db.close()

        return redirect("dashboard.html")
    except Exception as e:
        return f"Error uploading file: {e}"

# Run locally
if __name__ == "__main__":
    app.run(debug=True)
