#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Imports
import logging
import json
import os

# Thirt Party Imports
from dotenv import load_dotenv
from pymongo import MongoClient
from telegram import (ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Constants
LOCATION = 1
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MONGODB_URL = os.getenv("MONGODB_URL")

# Database connection
# mongoClient = MongoClient(MONGODB_URL)
# db = mongoClient.test_database


# read the json file
def read_data():
    with open('list.json', 'r') as f:
        data = json.load(f)

    return data


def start(update, context):
    user = update.message.from_user
    logger.info(f"{user.first_name}: {update.message.text}")
    update.message.reply_text(f"Olá, {user.first_name}")
    update.message.reply_text("Qual sua localização?")

    return LOCATION


def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    logger.info(f"{user.first_name}: "
                f"Location {user_location.latitude} / {user_location.longitude}")
    update.message.reply_text(f"Latitude:  {user_location.latitude}\n"
                              f"Longetude: {user_location.longitude}")

    return ConversationHandler.END


def skip_location(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'At last, tell me something about yourself.')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def list_all(update, content):
    user = update.message.from_user
    logger.info(f'User {user.first_name} solicited the order list.')
    update.message.reply_text('Lista de pedidos: ')
    order_list = read_data()

    final = ''
    for order in order_list:
        final += '%s (R$%s): \n\n' % (order['user'], float(order['price']))
        for p in order['pedido']:
            final += '- %s\n' % (p)
        final += '\n' + '-' * 10 + '\n'

    update.message.reply_text(final)


def get_all_prices(update, content):
    user = update.message.from_user
    logger.info(f'User {user.first_name} solicited all order prices.')

    order_list = read_data()
    final = ''
    for order in order_list:
        final += '*%s*\n- Total do pedido: *R$%s*\n\n' % (order['user'], float(order['price']))

    update.message.reply_text(final, parse_mode=ParseMode.MARKDOWN)


def get_price(update, content):
    user = update.message.from_user
    logger.info(f'User {user.first_name} solicited your order prices.')

    name = content.args[0]
    order_list = read_data()
    final = ''
    for order in order_list:
        if name.lower() in order['user'].lower():
            final += '*%s*\n- Total do pedido: *R$%s*\n\n' % (order['user'], float(order['price']))

    update.message.reply_text(final, parse_mode=ParseMode.MARKDOWN)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('list', list_all),
            CommandHandler('prices', get_all_prices),
            CommandHandler('price', get_price)
        ],
        states={
            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
