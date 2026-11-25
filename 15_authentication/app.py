from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, secrets, re
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"
DB = Path(__file__).with_name("users.db")

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL)''')

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(24)
    return session["csrf"]

@app.context_processor
def inject_csrf():
    return {"csrf_token": csrf_token}

def valid_csrf():
    return secrets.compare_digest(request.form.get("csrf", ""), session.get("csrf", ""))

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not valid_csrf():
            flash("Invalid form token. Please try again.", "error")
            return redirect(url_for("register"))
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", username):
            flash("Username must be 3–30 characters (letters, numbers or underscore).", "error")
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.", "error")
        elif len(password) < 8 or len(password) > 128:
            flash("Password must contain 8–128 characters.", "error")
        else:
            try:
                with connect() as db:
                    db.execute("INSERT INTO users(username,email,password_hash) VALUES(?,?,?)",
                               (username, email, generate_password_hash(password)))
                flash("Account created. You can now log in.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That username or email is already registered.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not valid_csrf():
            flash("Invalid form token. Please try again.", "error")
            return redirect(url_for("login"))
        identity = request.form.get("identity", "").strip()
        password = request.form.get("password", "")
        with connect() as db:
            user = db.execute("SELECT * FROM users WHERE username=? OR email=?",
                              (identity, identity.lower())).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("You are now logged in.")
            return redirect(url_for("home"))
        flash("Invalid username/email or password.", "error")
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    if valid_csrf():
        session.clear()
        flash("You have been logged out.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
