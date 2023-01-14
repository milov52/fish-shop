import os

import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram.ext import Filters, Updater

from cms_api import add_to_cart, delete_from_cart, get_cart, get_products

_database = None


def create_products_keyboard():
    keyboard = []
    buttons = []

    products = get_products()

    for index, product in enumerate(products):
        buttons.append(InlineKeyboardButton(product["name"], callback_data=product["id"]))
        if index % 2 == 0:
            keyboard.append(buttons)

    keyboard.append([InlineKeyboardButton('Корзина', callback_data='cart')])
    return keyboard


def start(bot, update):
    reply_markup = InlineKeyboardMarkup(create_products_keyboard())

    if update.message:
        update.message.reply_text(text="Please choice:", reply_markup=reply_markup)
    else:
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        update.callback_query.message.reply_text(text="Please choice:", reply_markup=reply_markup)

    return "HANDLE_MENU"


def menu(bot, update):
    query = update.callback_query

    if query.data == 'cart':
        cart_info(bot, update)
        return "HANDLE_MENU"
    elif query.data == 'back':
        start(bot, update)
        return "HANDLE_MENU"
    elif query.data.startswith('delete'):
        delete_items_from_cart(bot, update)
        return "HANDLE_MENU"

    product = get_products(query.data)
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

    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)

    bot.send_photo(query.message.chat_id,
                   image_path,
                   caption=detail,
                   reply_markup=InlineKeyboardMarkup(keyboard))

    return "HANDLE_DESCRIPTION"


def cart_info(bot, update):
    cart_info = get_cart(update.callback_query.message.chat_id)
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

    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)

    buttons.append([InlineKeyboardButton("В меню", callback_data='back')])

    bot.send_message(text=message,
                     chat_id=update.callback_query.message.chat_id,
                     reply_markup=InlineKeyboardMarkup(buttons))


def delete_items_from_cart(bot, update):
    item_id = update.callback_query.data.split(':')[1]
    cart_id = update.callback_query.message.chat_id
    delete_from_cart(cart_id, item_id)
    cart_info(bot, update)


def description(bot, update):
    query = update.callback_query

    if query.data == 'cart':
        cart_info(bot, update)
        return "HANDLE_DESCRIPTION"
    elif query.data == 'back':
        start(bot, update)
        return "HANDLE_MENU"
    elif query.data.startswith('delete'):
        delete_items_from_cart(bot, update)
        return "HANDLE_MENU"

    chat_id = update.callback_query.message.chat_id

    product_id = query.data.split(',')[0]
    count = int(query.data.split(',')[1])
    add_to_cart(chat_id, product_id, count)
    return "HANDLE_DESCRIPTION"


def handle_users_reply(bot, update):
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
        'HANDLE_MENU': menu,
        'HANDLE_DESCRIPTION': description,
        # 'HANDLE_CART': cart,
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
    db = get_database_connection()

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))

    updater.start_polling()
