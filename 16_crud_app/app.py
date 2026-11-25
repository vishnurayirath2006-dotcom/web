from flask import Flask, render_template, request, redirect, url_for, flash, abort
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"
DB = Path(__file__).with_name("records.db")

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS records(
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

def get_record(record_id):
    with connect() as db:
        row = db.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
    if row is None:
        abort(404)
    return row

@app.route("/")
def index():
    with connect() as db:
        records = db.execute("SELECT * FROM records ORDER BY id DESC").fetchall()
    return render_template("index.html", records=records)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not title or len(title) > 100 or len(description) > 1000:
        flash("Enter a title (max 100 characters) and a description (max 1000).", "error")
    else:
        with connect() as db:
            db.execute("INSERT INTO records(title,description) VALUES(?,?)", (title, description))
        flash("Record created.")
    return redirect(url_for("index"))

@app.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit(record_id):
    record = get_record(record_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title or len(title) > 100 or len(description) > 1000:
            flash("Please enter valid values.", "error")
        else:
            with connect() as db:
                db.execute("UPDATE records SET title=?, description=? WHERE id=?",
                           (title, description, record_id))
            flash("Record updated.")
            return redirect(url_for("index"))
    return render_template("edit.html", record=record)

@app.route("/delete/<int:record_id>", methods=["POST"])
def delete(record_id):
    get_record(record_id)
    with connect() as db:
        db.execute("DELETE FROM records WHERE id=?", (record_id,))
    flash("Record deleted.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
