import logging

import telegram
from environs import Env
from telegram import Update, BotCommand
from telegram.ext import CallbackContext, CommandHandler, Updater, MessageHandler, Filters

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    env = Env()
    env.read_env()
    bot_token = env.str('TG_TOKEN')
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher


    def error_handler(context: CallbackContext):
        logger.exception(msg="Произошло исключение", exc_info=context.error)

    def start(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Здравствуйте!')

    def echo(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    dp.add_handler(CommandHandler("start", start))
    dp.add_error_handler(error_handler)
    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
