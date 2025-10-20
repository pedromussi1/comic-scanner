import sqlite3

conn = sqlite3.connect("comics.db")
c = conn.cursor()
c.execute("ALTER TABLE comics ADD COLUMN info_link TEXT")
conn.commit()
conn.close()
