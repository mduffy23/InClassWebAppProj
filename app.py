"""
Lab Shop: a deliberately insecure Flask app for a classroom security workshop.

FOR TRAINING ONLY. Run it on your own machine, never deploy it, and never
expose it to a network. Do not reuse any code from this file in a real project.
"""

import hashlib
import os
import sqlite3

from flask import Flask, g, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "lab-secret-key-123"

API_KEY = "sk_live_Qm8vT3xLp0ZaN7rK2yWb9HcD"

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab.db")

HEADER = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Lab Shop</title></head>
<body style="font-family: sans-serif; max-width: 640px; margin: 2rem auto;">
<h1>Lab Shop</h1>
<nav>
  <a href="{{ url_for('index') }}">Home</a> |
  <a href="{{ url_for('search') }}">Search</a> |
  {% if session.get('user_id') %}
    <a href="{{ url_for('profile', user_id=session['user_id']) }}">My profile</a> |
    <a href="{{ url_for('logout') }}">Log out</a>
  {% else %}
    <a href="{{ url_for('login') }}">Log in</a>
  {% endif %}
</nav>
<hr>
"""

INDEX_BODY = """
<p>Welcome to the Lab Shop, a practice target for the security workshop.</p>
<p>Log in to view your profile, or try the search page.</p>
</body></html>
"""

LOGIN_BODY = """
<h2>Log in</h2>
{% if error %}<p style="color: #b00020;">{{ error }}</p>{% endif %}
<form method="post">
  <p><label>Username <input name="username" autofocus></label></p>
  <p><label>Password <input name="password" type="password"></label></p>
  <p><button type="submit">Log in</button></p>
</form>
</body></html>
"""

PROFILE_BODY = """
<h2>Profile</h2>
<table cellpadding="6">
  <tr><th align="left">ID</th><td>{{ user['id'] }}</td></tr>
  <tr><th align="left">Username</th><td>{{ user['username'] }}</td></tr>
  <tr><th align="left">Email</th><td>{{ user['email'] }}</td></tr>
  <tr><th align="left">Role</th><td>{{ user['role'] }}</td></tr>
  <tr><th align="left">Private note</th><td>{{ user['secret_note'] }}</td></tr>
</table>
</body></html>
"""

SEARCH_BODY = """
<h2>Search</h2>
<form method="get">
  <input name="q" placeholder="Search the shop">
  <button type="submit">Search</button>
</form>
"""


def md5_hex(text):
    return hashlib.md5(text.encode()).hexdigest()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            secret_note TEXT NOT NULL
        )
        """
    )
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        seed = [
            ("admin", md5_hex("admin123"), "admin@labshop.test", "admin",
             "LAB-FLAG{admin_secret_note}: payroll export is in /srv/exports (fake)"),
            ("alice", md5_hex("password1"), "alice@labshop.test", "customer",
             "Alice's private note: gift ideas for the holidays"),
            ("bob", md5_hex("letmein"), "bob@labshop.test", "customer",
             "Bob's private note: my locker combination reminder (fake)"),
        ]
        db.executemany(
            "INSERT INTO users (username, password_hash, email, role, secret_note) "
            "VALUES (?, ?, ?, ?, ?)",
            seed,
        )
        db.commit()
    db.close()


init_db()


@app.route("/")
def index():
    return render_template_string(HEADER + INDEX_BODY)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        pw_hash = md5_hex(password)
        db = get_db()
        user = db.execute(f"SELECT * FROM users WHERE username = '{username}' AND password_hash = '{pw_hash}'").fetchone()
        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("profile", user_id=user["id"]))
        error = "Invalid username or password."
    return render_template_string(HEADER + LOGIN_BODY, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/profile/<int:user_id>")
def profile(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = get_db().execute(
        "SELECT id, username, email, role, secret_note FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if user is None:
        return "User not found", 404
    return render_template_string(HEADER + PROFILE_BODY, user=user)


@app.route("/search")
def search():
    q = request.args.get("q", "")
    page = render_template_string(HEADER + SEARCH_BODY)
    if q:
        page += f"<p>No results found for: {q}</p>"
    return page + "</body></html>"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
