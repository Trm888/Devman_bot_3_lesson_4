import argparse
import logging
import os
import pathlib
import random
from logging.handlers import RotatingFileHandler

import redis
import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from get_questions_answers_script import get_questions_answers

logger = logging.getLogger(__name__)


def start_keyboard():
    keyboard_start = VkKeyboard(one_time=True)
    keyboard_start.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard_start.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)
    return keyboard_start.get_keyboard()


def continue_keyboard():
    keyboard_continue = VkKeyboard(one_time=True)
    keyboard_continue.add_button('Сдаться', color=VkKeyboardColor.POSITIVE)
    keyboard_continue.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)
    return keyboard_continue.get_keyboard()


def start(vk_api, event):
    vk_api.messages.send(
        user_id=event.user_id,
        message='🤜Привет я бот для викторин!🤛',
        random_id=random.randint(1, 1000),
        keyboard=start_keyboard(),
    )


def new_question(vk_api, event, redis_db, quiz_info):
    keyboard_continue = VkKeyboard(one_time=True)
    keyboard_continue.add_button('Сдаться', color=VkKeyboardColor.POSITIVE)
    keyboard_continue.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)
    random_question_answer = random.choice(list(quiz_info.items()))
    question = random_question_answer[0]
    answer = random_question_answer[1]
    redis_db.set('question', question)
    redis_db.set('answer', answer)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000),
        keyboard=continue_keyboard(),
    )


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(pathlib.PurePath.joinpath(pathlib.Path.cwd(), 'tg_bot.log'),
                                       maxBytes=100000,
                                       backupCount=3)
    file_handler.setFormatter(logging.Formatter('level=%(levelname)s time="%(asctime)s" message="%(message)s"'))
    logger.addHandler(file_handler)

    env = Env()
    env.read_env()
    vk_group_token = env.str('VK_API_KEY')
    host = env.str('REDIS_HOST')
    port = env.int('REDIS_PORT')
    redis_password = env.str('REDIS_PASSWORD')
    redis_db = redis.Redis(host=host, port=port, password=redis_password)
    if env.str('FILE_PATH'):
        default_file_path = env.str('FILE_PATH')
    else:
        default_file_path = (os.path.join(os.getcwd(), 'quiz-questions'))
    parser = argparse.ArgumentParser(description='Запуск скрипта')
    parser.add_argument(
        '-fp',
        '--file_path',
        help='Укажите путь к файлу',
        nargs='?', default=default_file_path, type=str
    )
    args = parser.parse_args()
    file_path = args.file_path
    questions_answers = get_questions_answers(filepath=file_path)

    while True:
        try:
            vk_session = vk.VkApi(token=vk_group_token)
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)
            logger.info('Бот запущен')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.text == "start":
                        start(vk_api, event)
                    elif event.text == "Сдаться":
                        vk_api.messages.send(
                            user_id=event.user_id,
                            message=f'Правильный ответ: {redis_db.get("answer").decode("utf-8")}',
                            random_id=random.randint(1, 1000),
                            keyboard=start_keyboard(),
                        )
                    elif event.text == 'Новый вопрос':
                        new_question(vk_api, event, redis_db, questions_answers)
                    else:
                        full_answer = redis_db.get('answer').decode('utf-8')
                        end_index = min(full_answer.find('('), full_answer.find('.'))
                        short_answer = full_answer[:end_index].strip().lower()
                        if event.text.strip().lower() == short_answer:
                            vk_api.messages.send(
                                user_id=event.user_id,
                                message='🎉Правильно! Поздравляю! Ты молодец!🎉',
                                random_id=random.randint(1, 1000),
                                keyboard=start_keyboard(),
                            )
                        else:
                            vk_api.messages.send(
                                user_id=event.user_id,
                                message='👎Не правильно! Попробуй еще раз!👎',
                                random_id=random.randint(1, 1000),
                                keyboard=continue_keyboard(),
                            )

        except Exception as error:
            logger.exception(f'Бот упал с ошибкой: {error}')
            continue


if __name__ == '__main__':
    main()
