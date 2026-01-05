from flask import Flask, render_template, request, redirect, session
import sqlite3
import cloudinary
import cloudinary.uploader
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# ===============================
# Cloudinary config (Render ENV)
# ===============================
cloudinary.config(
   cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# ===============================
# Database function
# ===============================
def get_db():
    return sqlite3.connect("database.db")

# ===============================
# Signup
# ===============================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except:
            return "Username already exists"
        conn.close()

        return redirect("/login")

    return render_template("signup.html")

# ===============================
# Login
# ===============================
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Login invalid"

    return render_template("login.html")

# ===============================
# Dashboard (LOGIN REQUIRED)
# ===============================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, url FROM notes")
    notes = cursor.fetchall()
    conn.close()

    is_admin = session["user"] == "admin"
    return render_template("dashboard.html", notes=notes, is_admin=is_admin)

# ===============================
# Upload (ADMIN ONLY)
# ===============================
@app.route("/upload", methods=["POST"])
def upload():
    if session.get("user") != "admin":
        return "Not allowed"

    file = request.files["file"]
    result = cloudinary.uploader.upload(file)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (filename, url) VALUES (?, ?)",
        (file.filename, result["secure_url"])
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ===============================
# Logout
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ===============================
# Run app
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
