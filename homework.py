import logging
import os
import sys
import time

import requests
import telegram

from dotenv import load_dotenv
from requests import RequestException
from http import HTTPStatus

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 600
# ENDPOINT = os.getenv('ENDPOINT')
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger.addHandler(logging.StreamHandler())


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(f'Удачная отправка сообщения в Telegram: {message}')
    except Exception as error:
        logger.error(f'Cбой при отправке сообщения в Telegram: {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса и возвращает ответ."""
    """Преобразовав его к типам данных Python."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_status = requests.get(
            ENDPOINT, headers=HEADERS, params=params)
        if homework_status.status_code != HTTPStatus.OK:
            logger.error('Недоступность эндпоинта')
            raise Exception('Недоступность эндпоинта')
    except RequestException:
        logger.error('Cбой при запросе к эндпоинту')
        raise RequestException('Cбой при запросе к эндпоинту')
    return homework_status.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    homeworks = response['homeworks']
    try:
        'homeworks' and 'current_date' in response['homeworks']
    except KeyError as error:
        logger.error(f'Отсутствие ожидаемых ключей в ответе API: {error}')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Неверный тип ответа API')
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе ее статус."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES.keys():
        raise KeyError('Такого статуса нет')
    else:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют переменные окружения!')
        raise SystemExit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if isinstance(homework, list) and homework:
                send_message(bot, parse_status(homework))
            else:
                logger.debug('Oтсутствие в ответе новых статусов')
                # send_message(bot, message = 'Нет обновлений')
            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Выход из программы')
        sys.exit(0)
