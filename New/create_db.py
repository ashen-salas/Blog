import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    image_url TEXT
)
''')

admin_user = 'ashen'
admin_pass = '159456'
password_hash = generate_password_hash(admin_pass)

try:
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (admin_user, password_hash))
    print('Usuario admin creado: ashen / 159456')
except sqlite3.IntegrityError:
    print('Usuario admin ya existe.')

conn.commit()
conn.close()
