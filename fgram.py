#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from telegram import (ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LOCATION = 1


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


def main():
    telegram_token = ""

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

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