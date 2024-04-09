import sqlite3

dbname = 'SOUZAI.db'
conn = sqlite3.connect(dbname)

cur = conn.cursor()

cur.execute('CREATE TABLE foods(id INTEGER PRIMARY KEY AUTOINCREMENT,name STRING)')

cur.execute('''
CREATE TABLE IF NOT EXISTS times (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    time TEXT NOT NULL
)
''')


conn.commit()
conn.close()
