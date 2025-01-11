import sqlite3

con = sqlite3.connect("test1.db")
cur = con.cursor()

# створити БД ---------------------------
# cur.execute('CREATE TABLE user(name, year, title);')
# cur.execute(''' CREATE TABLE user_1(
#         id INTEGER PRIMARY KEY,
#         name TEXT DEFAULT 'Невідомий',
#         year INTEGER DEFAULT 0,
#         title TEXT NOT NULL
#     );''')
#
#
# con.commit()
name = 'ілля'
year = 87
title = 'зміни'

# Додати до ДБ інформацію
cur.execute(f"""INSERT INTO user_1 (name, year, title)
    VALUES (?, ?, ?);""", (name, year, title))
con.commit()

con.close()