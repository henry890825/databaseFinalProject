import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('CREATE TABLE User (name text, password text)')
print('created table successfully')

conn.execute('CREATE TABLE Rating (uId integer, fId integer, score real, date text, comment text, pic blob)')
print('created table successfully')

conn.execute('CREATE TABLE Food (food_sId integer, name text, price integer)')
print('created table successfully')

conn.execute('CREATE TABLE Store (name text, addr text)')
print('created table successfully')

conn.close()
