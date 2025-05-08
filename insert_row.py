import sqlite3

conn = sqlite3.connect('database.db')

# conn.execute('INSERT INTO User VALUES("henry", "123")')

conn.commit()
conn.close()
