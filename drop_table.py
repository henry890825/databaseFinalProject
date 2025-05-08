import sqlite3

conn = sqlite3.connect('database.db')

# conn.execute('DROP TABLE user')
# print('droped table successfully')

conn.close()

