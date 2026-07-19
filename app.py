from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'linux_assignment_key' # সেশন সুরক্ষিত রাখার জন্য

# ১. ডাটাবেস টেবিল চেক ও তৈরি করার ফাংশন (যা আগে fix_db.py এ ছিল)
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # items টেবিলটি তৈরি করা যদি না থাকে
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ২. লগইন সিস্টেম
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['logged_in'] = True
            return redirect(url_for('index'))
    return '''
        <form method="post" style="text-align:center;margin-top:50px;">
            <h2>Login to Linux Server</h2>
            User: <input name="username"><br><br>
            Pass: <input name="password" type="password"><br><br>
            <button type="submit">Login</button>
        </form>
    '''

# ৩. ড্যাশবোর্ড (Read Operation)
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('dashboard.html', items=items)

# ৪. ডাটা যোগ করা (Create)
@app.route('/add', methods=['POST'])
def add():
    content = request.form['content']
    conn = get_db_connection()
    conn.execute('INSERT INTO items (content) VALUES (?)', (content,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ৫. ডাটা এডিট করা (Update)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('UPDATE items SET content = ? WHERE id = ?', (request.form['content'], id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    item = conn.execute('SELECT * FROM items WHERE id = ?', (id,)).fetchone()
    conn.close()
    return f'<form method="post">Update Data: <input name="content" value="{item["content"]}"><button>Save</button></form>'

# ৬. ডাটা মুছে ফেলা (Delete)
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db() # সার্ভার চালুর সময় ডাটাবেস নিশ্চিত করবে
    app.run(host='0.0.0.0', port=5000, debug=True)

