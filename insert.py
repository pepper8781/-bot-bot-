import sqlite3

dbname = 'SOUZAI.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

cur.execute('INSERT INTO foods(name) values("からあげ")')
cur.execute('INSERT INTO foods(name) values("ハンバーグ")')
cur.execute('INSERT INTO foods(name) values("とんかつ")')
cur.execute('INSERT INTO foods(name) values("肉を甘辛く炒めたやつ")')
cur.execute('INSERT INTO foods(name) values("おひたし")')
cur.execute('INSERT INTO foods(name) values("アジフライ")')
cur.execute('INSERT INTO foods(name) values("甘酢の餡がかかってるやつ")')
cur.execute('INSERT INTO foods(name) values("エビチリ")')
cur.execute('INSERT INTO foods(name) values("メンチカツ")')
cur.execute('INSERT INTO foods(name) values("肉じゃが")')
cur.execute('INSERT INTO foods(name) values("ごぼうとにんじん炒めたやつ")')
cur.execute('INSERT INTO foods(name) values("きんぴらごぼう")')


cur.execute('ALTER TABLE times ADD COLUMN is_loop INTEGER DEFAULT 0;')

conn.commit()

cur.close()
conn.close()