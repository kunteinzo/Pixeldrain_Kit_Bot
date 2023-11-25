import os
import re
import sqlite3

import telebot
from telebot.types import Message, User

bot = telebot.TeleBot(os.environ.get('TOKEN'))

print('Bot is running...')

    
def db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            create table if not exists User
            (
            id integer,
            username text,
            full_name text
            );""")
        cursor.execute("""
            create table if not exists Keys
            (
            id integer primary key autoincrement,
            uid integer,
            apikey text,
            foreign key (uid) references User(id)
            );"""
        )
        conn.commit()
        return conn
        
        
def add_user(user: User):
    with db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "insert into User (id,username,full_name) values (?,?,?);",
            (user.id, user.username, user.full_name)
        )
        conn.commit()
        
        
def mykey(user: User):
    with db() as conn:
        return conn.cursor().execute("select * from Keys where uid=?;", (user.id,)).fetchall()


def is_not_exist(user: User):
    with db() as conn:
        return conn.cursor().execute("select * from User where id=?", (user.id,)).fetchone() is None
        
        
def add_apikey(user: User, key: str):
    with db() as conn:
        if is_key_not_valid(key):
            return False
        cursor = conn.cursor()
        if cursor.execute('select * from Keys where apikey=?;', (key,)).fetchone() is None:
            cursor.execute(
                "insert into Keys (uid, apikey) values (?,?);",
                (user.id, key)
            )
        conn.commit()
        return True


def is_key_not_valid(key: str):
    return re.match('^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', key) is None


@bot.message_handler(commands=['start'])
def start(message: Message):
    user = message.from_user
    if is_not_exist(user):
        add_user(user)
    bot.send_message(message.chat.id, f"Hello *{user.full_name}*\.", 'MarkdownV2')


@bot.message_handler(commands=['addkey'])
def addkey(message: Message):
    key = message.text[8:].strip()
    if is_key_not_valid(key):
        bot.send_message(message.chat.id, "Your Key is invalid.")
        return
    with db() as conn:
        cursor = conn.cursor()
        if cursor.execute("select * from Keys where apikey=?;", (key,)) is None:
            cursor.execute("insert into Keys (uid, apikey) values (?,?);", (message.from_user.id, key))
            conn.commit()
        bot.send_message(message.chat.id, "Your Key have been added.")


@bot.message_handler(commands=['mykey'])
def my_key(message: Message):
    keys = "\n".join(["`"+id+"` - `"+apikey.replace("-","\-")+"`" for id,_,apikey in mykey(message.from_user)])
    bot.send_message(message.chat.id, f"Your keys are {keys}", 'MarkdownV2')


bot.infinity_polling()
