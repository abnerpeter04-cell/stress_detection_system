import sqlite3

conn = sqlite3.connect('users.db')

cursor = conn.cursor()

# USERS TABLE
cursor.execute('''

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    password TEXT
)

''')

# PREDICTIONS TABLE
cursor.execute('''

CREATE TABLE IF NOT EXISTS predictions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    study_hours REAL,

    sleep_hours REAL,

    break_frequency REAL,

    prediction TEXT,

    date TEXT
)

''')

conn.commit()

conn.close()

print("Database created successfully.")