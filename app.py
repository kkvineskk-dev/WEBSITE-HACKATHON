from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai

# ----------------- LOAD ENVIRONMENT VARIABLES -----------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ No Gemini API key found! Please add your key in a .env file like this:")
    print("GEMINI_API_KEY=AIzaSyBjgCEkhLJPDvkIu0HZOoXGfkGXpd2Qi7E")
else:
    genai.configure(api_key="AIzaSyBjgCEkhLJPDvkIu0HZOoXGfkGXpd2Qi7E")
    print("✅ Gemini AI configured successfully!")

# ----------------- FLASK APP SETUP -----------------
app = Flask(__name__)
app.secret_key = "supersecretkey"

# ----------------- DATABASE SETUP -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "experion.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS internships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        project_title TEXT NOT NULL,
        description TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()

# Initialize DB
init_db()
print("✅ Database initialized successfully!")

# ----------------- ROUTES -----------------

@app.route('/')
def home():
    return render_template('index.html')

# ---------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("✅ Signup successful! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("⚠️ Username already exists!", "warning")
        finally:
            conn.close()

    return render_template('signup.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['username'] = username
            flash(f"👋 Welcome back, {username}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("❌ Invalid username or password!", "danger")

    return render_template('login.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM submissions WHERE username=?", (username,))
    submissions = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', username=username, submissions=submissions)

# ---------- INTERNSHIPS ----------
@app.route('/internships')
def internships():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM internships")
    internships = cur.fetchall()
    conn.close()
    return render_template('internships.html', internships=internships)

# ---------- SUBMIT PROJECT ----------
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        username = session['username']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO submissions (username, project_title, description) VALUES (?, ?, ?)",
            (username, title, description)
        )
        conn.commit()
        conn.close()

        flash("✅ Project submitted successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('submit.html')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("👋 You have been logged out.", "info")
    return redirect(url_for('login'))

# ---------- AI ASSISTANT PAGE ----------
@app.route('/assistant')
def assistant_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('assistant.html')

# ---------- AI API ENDPOINT (Gemini) ----------
@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    data = request.get_json()
    user_query = data.get("query", "")

    if not GEMINI_API_KEY:
        return jsonify({"answer": "⚠️ AI not configured. Add your Gemini API key in .env."})

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_query)
        answer = response.text.strip()
    except Exception as e:
        answer = f"⚠️ Error: {str(e)}"

    return jsonify({"answer": answer})

# ---------- ERROR HANDLER ----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ---------- RUN SERVER ----------
if __name__ == '__main__':
    app.run(debug=True)
