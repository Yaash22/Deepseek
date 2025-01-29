from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['DATABASE'] = 'database.db'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
def init_db():
    with sqlite3.connect(app.config['DATABASE']) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_date TEXT NOT NULL
            )
        ''')

# Home page
@app.route('/')
def index():
    with sqlite3.connect(app.config['DATABASE']) as conn:
        documents = conn.execute('SELECT * FROM documents').fetchall()
    return render_template('index.html', documents=documents)

# Upload file
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(app.config['DATABASE']) as conn:
            conn.execute('INSERT INTO documents (filename, upload_date) VALUES (?, ?)', (filename, upload_date))
        return redirect(url_for('index'))

# Download file
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)