import os
import logging
import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from cms_api import get_products

_database = None
_keyboard = []

def start(bot, update):
    products = get_products()
    buttons = []
    for index, product in enumerate(products):
        buttons.append(InlineKeyboardButton(product.get("name"), callback_data=product.get("id")))
        if index % 2 == 0:
            _keyboard.append(buttons)

    reply_markup = InlineKeyboardMarkup(_keyboard)
    update.message.reply_text(text="Please choice:", reply_markup=reply_markup)
    return "CHOICE"


def button(bot, update):
    query = update.callback_query
    reply_markup = InlineKeyboardMarkup(_keyboard)
    bot.edit_message_text(text='Selected options: {}'.format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup)
    return "CHOICE"

def echo(bot, update):
    users_reply = update.message.text
    update.message.reply_text(users_reply)
    return "ECHO"

def handle_users_reply(bot, update):
    db = get_database_connection()

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode('utf-8')


    states_functions = {
        'START': start,
        'CHOICE': button,
        'ECHO': echo
    }

    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)

def get_database_connection():
    global _database
    if _database is None:
        database_password = os.environ.get("DATABASE_PASSWORD")
        database_host = os.environ.get("DATABASE_HOST")
        database_port = os.environ.get("DATABASE_PORT")

        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    load_dotenv()
    token = os.environ.get("TELEGRAM_TOKEN")

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()

