from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'super_secret_ai_hacker_key' # Session ke liye zaruri hai

# 🔴 ADMIN CREDENTIALS (Yahan se aap apna ID Password change kar sakte hain)
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, yt_id TEXT)''')
    conn.commit()
    conn.close()

def get_yt_id(url):
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return match.group(1) if match else url

# --- ROUTES ---

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    videos = conn.execute('SELECT * FROM videos ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == ADMIN_USER and pwd == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Galat Username ya Password! ❌')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    videos = conn.execute('SELECT * FROM videos ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', videos=videos)

@app.route('/add', methods=['POST'])
def add_video():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    title = request.form['title']
    desc = request.form['description']
    link = request.form['link']
    yt_id = get_yt_id(link)
    
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO videos (title, description, yt_id) VALUES (?, ?, ?)', (title, desc, yt_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
def delete_video(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    conn.execute('DELETE FROM videos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
