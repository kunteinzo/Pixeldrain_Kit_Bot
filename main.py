import json
import os
import re
import sqlite3

import requests
import telebot
from telebot.types import Message, User, CallbackQuery

import db
from pixeldrain import post_file, get_file

bot = telebot.TeleBot(os.environ.get('TOKEN'))

print('Bot is running...')


# user configuration
@bot.message_handler(commands=['start'])
def start(message: Message):
    user = message.from_user
    db.add(user.id)
    bot.send_message(message.chat.id, f"Hello *{user.full_name}*\.\nWould you like to add your Pixeldrain API Key\?",
                     'MarkdownV2',
                     reply_markup=telebot.util.quick_markup(
                         {
                             'Yes': {
                                 'callback_data': 'btn_yes'
                             },
                             'No': {
                                 'callback_data': 'btn_no'
                             }
                         }
                     ))


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    msg = ''
    markup = telebot.util.quick_markup(
        {
            'OK, I\'ll add later.': {
                'callback_data': 'btn_later'
            }
        }
    )
    if call.data == 'btn_yes':
        bot.register_next_step_handler(call.message, add_user_token)
        msg = "Now, send your token."
        markup = None
    elif call.data == 'btn_no':
        msg = "Your know what, You can add it later."
    elif call.data == 'btn_later':
        bot.delete_message(call.message.chat.id, call.message.id)
        return
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.message_handler(commands=['addtoken'])
def add_user_token(message: Message):
    """
    Add user's token to database.
    :param message:
    :return:
    """
    token = message.text.strip()
    add = '/addtoken'
    msg = "Your token has been added successfully."
    if add == token:
        # if click manual, send token later
        bot.send_message(message.chat.id, "Now, send your token.")
        bot.register_next_step_handler(message, add_user_token)
        return
    if add in token:
        # if cmd with token split it and check, add if valid
        token = token.replace(add, '').strip()
    if not db.add(message.from_user.id, token):
        msg = "Your token is invalid!"
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['mytoken'])
def user_token(message: Message):
    token = db.get_token(message.from_user.id).replace("-", "\-")
    msg = f'Your token is `{token}`'
    if not token:
        msg = "Your don't have token"
    bot.send_message(message.chat.id, msg, 'MarkdownV2')


@bot.message_handler(commands=['deltoken'])
def del_user_token(message: Message):
    db.del_token(message.from_user.id)
    bot.send_message(message.chat.id, "Your token has been deleted.")


# pixeldrain configuration
@bot.message_handler(content_types=['photo', 'document'])
def upload_photo(message: Message):
    if message.photo:
        token = db.get_token(message.from_user.id)
        path = bot.get_file(message.photo[-1].file_id).file_path
        print(path)
        print(path.replace(re.match("[a-z]+\/", path).group(), ''))


@bot.message_handler(commands=['getphoto'])
def get_photo(message: Message):
    file_id = message.text[10:].strip()
    r = get_file(file_id)
    if r.status_code == 200:
        bot.send_photo(message.chat.id, r.content)


bot.infinity_polling()
