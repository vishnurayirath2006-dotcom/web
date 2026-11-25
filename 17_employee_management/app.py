from flask import Flask, render_template, request, redirect, url_for, flash, abort
import sqlite3, re
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"
DB = Path(__file__).with_name("employees.db")

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT NOT NULL, department TEXT NOT NULL, role TEXT NOT NULL,
            salary REAL NOT NULL CHECK(salary >= 0))''')

def employee_data(form):
    name = form.get("name", "").strip()
    email = form.get("email", "").strip()
    department = form.get("department", "").strip()
    role = form.get("role", "").strip()
    salary_text = form.get("salary", "").strip()
    if not all([name, email, department, role, salary_text]):
        raise ValueError("All fields are required.")
    if len(name) > 80 or len(department) > 60 or len(role) > 60:
        raise ValueError("Name, department or role is too long.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Enter a valid email address.")
    try:
        salary = float(salary_text)
        if salary < 0 or salary > 100000000:
            raise ValueError
    except ValueError:
        raise ValueError("Salary must be a valid non-negative number.")
    return name, email, department, role, salary

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    with connect() as db:
        if q:
            if q.isdigit():
                rows = db.execute("SELECT * FROM employees WHERE name LIKE ? OR id=? ORDER BY id DESC",
                                  (f"%{q}%", int(q))).fetchall()
            else:
                rows = db.execute("SELECT * FROM employees WHERE name LIKE ? OR department LIKE ? OR role LIKE ? ORDER BY id DESC",
                                  (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
        else:
            rows = db.execute("SELECT * FROM employees ORDER BY id DESC").fetchall()
    return render_template("index.html", employees=rows, q=q)

@app.route("/add", methods=["POST"])
def add():
    try:
        data = employee_data(request.form)
        with connect() as db:
            db.execute("INSERT INTO employees(name,email,department,role,salary) VALUES(?,?,?,?,?)", data)
        flash("Employee added successfully.")
    except ValueError as e:
        flash(str(e), "error")
    except sqlite3.IntegrityError:
        flash("Could not save this employee. Check the entered data.", "error")
    return redirect(url_for("index"))

@app.route("/edit/<int:employee_id>", methods=["GET", "POST"])
def edit(employee_id):
    with connect() as db:
        employee = db.execute("SELECT * FROM employees WHERE id=?", (employee_id,)).fetchone()
    if employee is None:
        abort(404)
    if request.method == "POST":
        try:
            data = employee_data(request.form)
            with connect() as db:
                db.execute("UPDATE employees SET name=?,email=?,department=?,role=?,salary=? WHERE id=?",
                           (*data, employee_id))
            flash("Employee updated.")
            return redirect(url_for("index"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("edit.html", employee=employee)

@app.route("/delete/<int:employee_id>", methods=["POST"])
def delete(employee_id):
    with connect() as db:
        db.execute("DELETE FROM employees WHERE id=?", (employee_id,))
    flash("Employee deleted.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
