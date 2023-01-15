import os
from functools import partial

import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram.ext import Filters, Updater

import cms_api

_database = None


def create_keyboard_2_columns(products):
    keyboard = []
    buttons = []

    for index, product in enumerate(products):
        buttons.append(InlineKeyboardButton(product["name"],
                                            callback_data=product["id"]))
        if index % 2 == 0:
            keyboard.append(buttons)

    keyboard.append([InlineKeyboardButton('Корзина',
                                          callback_data='cart')])
    return keyboard


def start(bot, update, client_id):
    products = cms_api.get_products(client_id=client_id)
    reply_markup = InlineKeyboardMarkup(create_keyboard_2_columns(products))

    if update.message:
        update.message.reply_text(text="Please choice:", reply_markup=reply_markup)
    else:
        update.callback_query.message.reply_text(text="Please choice:", reply_markup=reply_markup)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
    return "HANDLE_MENU"


def handle_menu(bot, update, client_id):
    query = update.callback_query

    if query.data == 'cart':
        view_cart(bot, update, client_id)
        return "HANDLE_CART"

    product = cms_api.get_product(product_id=query.data, client_id=client_id)
    image_path = product["image_path"]

    name = product["name"]
    description = product["description"]
    price = product["price"]
    stock = product["stock"]

    detail = f'{name}\n\n Стоимость: {price}\n В наличии: {stock}\n\n {description}'

    keyboard = [[InlineKeyboardButton("Назад", callback_data='back')],
                [
                    InlineKeyboardButton("1 шт", callback_data=f"{query.data},1"),
                    InlineKeyboardButton("2 шт", callback_data=f"{query.data},2"),
                    InlineKeyboardButton("5 шт", callback_data=f"{query.data},5")
                ],
                [InlineKeyboardButton('Корзина', callback_data='cart')]
                ]

    bot.send_photo(query.message.chat_id,
                   image_path,
                   caption=detail,
                   reply_markup=InlineKeyboardMarkup(keyboard))

    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)

    return "HANDLE_DESCRIPTION"


def generate_cart(bot, update, client_id):
    chat_id = update.callback_query.message.chat_id
    cart_info = cms_api.get_cart(chat_id, client_id)
    message = ''
    buttons = []

    for item in cart_info["cart_items"]:
        message += f'{item["name"]}\n\n' \
                   f'{item["description"][:100]}\n\n' \
                   f'Price: {item["price"]}\n' \
                   f'{item["quantity"]} in cart on {item["amount"]}\n\n'

        buttons.append([InlineKeyboardButton(f'Убрать из корзины {item["name"]}',
                                             callback_data=f'delete:{item["id"]}')])

    message += f'Full amount: {cart_info["full_amount"]}'

    buttons.append([InlineKeyboardButton("В меню", callback_data='back')])
    buttons.append([InlineKeyboardButton("Оплатить", callback_data='pay')])

    reply_markup = InlineKeyboardMarkup(buttons)
    return message, reply_markup


def view_cart(bot, update, client_id):
    query = update.callback_query

    if query.data == 'back':
        start(bot, update, client_id)
        return "HANDLE_MENU"
    elif query.data.startswith('delete'):
        item_id = _, query.data.split(':')
        cart_id = query.message.chat_id
        cms_api.delete_from_cart(cart_id, item_id, client_id)
        generate_cart(bot, update, client_id)
    elif query.data == 'pay':
        bot.send_message(text='Пришлите адрес электронной почты:',
                         chat_id=update.callback_query.message.chat_id)
        return "WAITING_EMAIL"

    message, reply_markup = generate_cart(bot, update, client_id)
    bot.send_message(text=message,
                     chat_id=update.callback_query.message.chat_id,
                     reply_markup=reply_markup)
    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)
    return "HANDLE_CART"


def waiting_email(bot, update, client_id):
    email = update.message.text
    chat_id = update.message.chat_id
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("В меню", callback_data='back')]
    ])

    bot.send_message(text=f'Ваш email: {email} сохранен',
                     chat_id=chat_id,
                     reply_markup=keyboard)
    cms_api.create_user_account(str(chat_id), email, client_id)
    return "START"


def handle_description(bot, update, client_id):
    query = update.callback_query

    if query.data == 'cart':
        view_cart(bot, update, client_id)
        return "HANDLE_CART"
    elif query.data == 'back':
        start(bot, update, client_id)
        return "HANDLE_MENU"

    chat_id = update.callback_query.message.chat_id

    product_id, count = query.data.split(',')
    cms_api.add_to_cart(chat_id, product_id, int(count), client_id)
    return "HANDLE_DESCRIPTION"


def handle_users_reply(bot, update, client_id):
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
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': view_cart,
        'WAITING_EMAIL': waiting_email,
    }

    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update, client_id)
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
    client_id = os.environ.get("CLIENT_ID")

    db = get_database_connection()

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', partial(handle_users_reply, client_id=client_id)))
    dispatcher.add_handler(CallbackQueryHandler(partial(handle_users_reply, client_id=client_id)))
    dispatcher.add_handler(MessageHandler(Filters.text, partial(handle_users_reply, client_id=client_id)))

    updater.start_polling()
