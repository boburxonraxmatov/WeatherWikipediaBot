import sqlite3
import psycopg2

database = sqlite3.connect('ls5.db')

cursor = database.cursor()


cursor.execute('''
CREATE TABLE weather (
    weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
    temp TEXT,
    wind TEXT,
    name TEXT,
    description TEXT,
    sunrise TEXT,
    sunset TEXT
);
''')

database.close()



# database = psycopg2.connect(
#     database='ls5',
#     host='localhost',
#     user='postgres',
#     password='123456'
# )
#
# cursor = database.cursor()
#
# cursor.execute(
# '''CREATE TABLE IF NOT EXISTS weather(
#
# weather_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
# temp TEXT,
# wind TEXT,
# name TEXT,
# description TEXT,
# sunrise TEXT,
# sunset TEXT
#
# )'''
# )
#
# database.commit()
# database.close()
