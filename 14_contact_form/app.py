from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"
DB = Path(__file__).with_name("contacts.db")

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS contacts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL, message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please complete every field.", "error")
        elif len(name) > 80 or len(email) > 120 or len(message) > 2000:
            flash("One or more fields are too long.", "error")
        elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            flash("Enter a valid email address.", "error")
        else:
            with connect() as db:
                db.execute("INSERT INTO contacts(name,email,message) VALUES(?,?,?)",
                           (name, email, message))
            flash("Your message was submitted successfully.")
            return redirect(url_for("index"))
    return render_template("index.html")

@app.route("/messages")
def messages():
    with connect() as db:
        rows = db.execute("SELECT * FROM contacts ORDER BY id DESC").fetchall()
    return render_template("messages.html", rows=rows)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
