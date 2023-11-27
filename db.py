import re
import sqlite3


def is_token_valid(token: str):
    return re.match('^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', token) is not None


def db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
        create table if not exists User (
        id integer not null,
        token text deault '');
        """)
        conn.commit()
        return conn


def add(user_id, token: str = ''):
    with db() as conn:
        cursor = conn.cursor()
        if cursor.execute("select * from User where id=?;", (user_id,)).fetchone() is None:
            cursor.execute("insert into User (id, token) values (?,?);", (user_id, token))
        elif is_token_valid(token):
            cursor.execute("update User set token=? where id=?;", (token, user_id))
        else:
            return None
        conn.commit()
        return True


def get_token(user_id):
    with db() as conn:
        user = conn.cursor().execute("select * from User where id=?;", (user_id,)).fetchone()
        if user is None or user[1] == '':
            return None
        return str(user[1])


def del_token(user_id):
    with db() as conn:
        conn.cursor().execute("update User set token='' where id=?;", (user_id,))
        conn.commit()
