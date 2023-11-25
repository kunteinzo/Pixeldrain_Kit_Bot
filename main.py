import os
import re
import sqlite3

import telebot
from telebot.types import Message, User

bot = telebot.TeleBot(os.environ.get('TOKEN'))

print('Bot is running...')


def udb():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "create table if not exists User"
            "("
            "id integer,"
            "username text,"
            "first_name text,"
            "last_name text,"
            "full_name text"
            ");"
        )
        cursor.execute(
            "create table if not exists Key"
            "("
            "uid integer,"
            "apikey text,"
            "foreign key (uid) references User(id)"
            ");"
        )
        conn.commit()
        return conn


def add_user(user: User):
    with udb() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "insert into User (id,username,first_name,last_name,full_name) values (?,?,?,?,?);",
            (user.id, user.username, user.first_name, user.last_name, user.full_name)
        )
        conn.commit()


def is_not_exist(user: User):
    with udb() as conn:
        return conn.cursor().execute("select * from User where id=?", (user.id,)) is None


def is_key_not_valid(key: str):
    return re.match('^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', key) is None


def add_apikey(user: User, key: str):
    if is_key_not_valid(key):
        return False
    with udb() as conn:
        cursor = conn.cursor()
        if cursor.execute('select * from Key where apikey=?;', (key,)).fetchone() is None:
            cursor.execute(
                "insert into Key (uid, apikey) values (?,?);",
                (user.id, key)
            )
        conn.commit()
        return True


@bot.message_handler(commands=['start'])
def start(message: Message):
    user = message.from_user
    if is_not_exist(user):
        add_user(user)
    bot.send_message(message.chat.id, f"Hello *{user.full_name}*\.", 'MarkdownV2')


@bot.message_handler(commands=['add_key'])
def add_key(message: Message):
    key = message.text[9:].strip()
    if add_apikey(message.from_user, key):
        bot.send_message(message.chat.id, "Your key is added successfully.")
    else:
        bot.send_message(message.chat.id, "Failed to add your key.")


@bot.message_handler(commands=['my_key'])
def my_key(message: Message):
    with udb() as conn:
        cursor = conn.cursor()
        kk = cursor.execute(
            "select * from Key where uid=?;",
            (message.from_user.id,)
        ).fetchall()
        keys = '\n'.join([("`" + apikey.replace('-', '\-') + "`") for _, apikey in kk])
        bot.send_message(message.chat.id, f"Your key are \n{keys}", 'MarkdownV2')


@bot.message_handler(commands=['delete_key'])
def delete_key(message: Message):
    key = message.text[9:].strip()
    if is_key_not_valid(key):
        bot.send_message(message.chat.id, 'Api Key not valid.')
        return
    with udb() as conn:
        cursor = conn.cursor()
        cursor.execute("delete from Key where apikey=?", (key,))
        conn.commit()


bot.infinity_polling()
