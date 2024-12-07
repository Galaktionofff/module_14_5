import sqlite3


connection = sqlite3.connect('banki.db')
cursor = connection.cursor()


def initiate_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INT NOT NULL
    )
    ''')
    connection.commit()


def initiate_users_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT,
        age INT NOT NULL,
        balance INT
        )
        ''')
    connection.commit()


def add_user(username, email, age):
    cursor.execute(f'''
    INSERT INTO Users (username, email, age, balance) VALUES('{username}', '{email}', '{age}', '{1000}')''')
    connection.commit()


def is_included(username):
    check_user = cursor.execute('SELECT * FROM Users WHERE username = ?', (username,)).fetchone()
    connection.commit()
    return bool(check_user)


def get_all_products():
    cursor.execute('SELECT * FROM Products')
    all_ = cursor.fetchall()
    connection.commit()
    return all_
