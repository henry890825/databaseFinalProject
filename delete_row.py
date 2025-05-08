import sqlite3

conn = sqlite3.connect('database.db')

# conn.execute('DELETE FROM Rating WHERE rowid = (?)', ('10',))

conn.commit()
conn.close()
