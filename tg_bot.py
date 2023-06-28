import logging
import random

import redis
import telegram
from environs import Env
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CommandHandler, Updater, CallbackQueryHandler, MessageHandler, Filters, \
    ConversationHandler

from utils import get_questions_answers

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    quiz = get_questions_answers()
    env = Env()
    env.read_env()
    bot_token = env.str('TG_TOKEN')
    host = env.str('REDIS_HOST')
    port = env.int('REDIS_PORT')
    redis_password = env.str('REDIS_PASSWORD')
    redis_db = redis.Redis(host=host, port=port, password=redis_password)

    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    START = 1

    def error_handler(update: Update, context: CallbackContext):
        logger.exception(msg="Произошло исключение", exc_info=context.error)

    def start(update: Update, context: CallbackContext):
        redis_db.set('user_id', update.effective_chat.id)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='<b>🤜Привет я бот для викторин!🤛</b>',
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text='Новый вопрос', callback_data='new_question')],
                    [InlineKeyboardButton(text='Мой счет', callback_data='my_score')],
                ]
            )
        )
        return ConversationHandler.END

    def new_question(update: Update, context: CallbackContext):
        random_question_answer = random.choice(list(quiz.items()))
        question = random_question_answer[0]
        redis_db.set('question', question)
        redis_db.set('answer', random_question_answer[1])
        update.callback_query.edit_message_text(question, parse_mode=telegram.ParseMode.HTML,
                                                reply_markup=InlineKeyboardMarkup(
                                                    [
                                                        [InlineKeyboardButton(text='Сдаться',
                                                                              callback_data='give_up')],
                                                        [InlineKeyboardButton(text='Мой счет',
                                                                              callback_data='my_score')],
                                                    ]
                                                ))
        return START

    def give_up(update: Update, context: CallbackContext):
        full_answer = redis_db.get('answer').decode('utf-8')
        update.callback_query.edit_message_text(f'<b>Правильный ответ: {full_answer}',
                                                reply_markup=InlineKeyboardMarkup(
                                                    [
                                                        [InlineKeyboardButton(text='Новый вопрос',
                                                                              callback_data='new_question')],
                                                        [InlineKeyboardButton(text='Мой счет',
                                                                              callback_data='my_score')],
                                                    ]
                                                ))
        return ConversationHandler.END

    def answer(update: Update, context: CallbackContext):
        full_answer = redis_db.get('answer').decode('utf-8')
        end_index = min(full_answer.find('('), full_answer.find('.'))
        short_answer = full_answer[:end_index].strip().lower()
        if update.message.text.strip().lower() == short_answer:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='🎉Правильно! Поздравляю! Ты молодец!🎉',
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(text='Новый вопрос', callback_data='new_question'),
                         InlineKeyboardButton(text='Сдаться', callback_data='give_up')],
                        [InlineKeyboardButton(text='Мой счет', callback_data='my_score')],
                    ]
                )
            )
            return ConversationHandler.END
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='👎Не правильно! Попробуй еще раз!👎',
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(text='Сдаться', callback_data='give_up')],
                        [InlineKeyboardButton(text='Мой счет', callback_data='my_score')],
                    ]
                )
            )

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_question, pattern='new_question')],
        states={
            START: [
                MessageHandler(Filters.text & (~Filters.command), answer),
            ],
        },
        fallbacks=[CommandHandler("start", start), CallbackQueryHandler(give_up, pattern='give_up')],
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
