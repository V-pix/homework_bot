import logging
import os
import sys
import time
from http import HTTPStatus
from json.decoder import JSONDecodeError

import requests
import telegram
from dotenv import load_dotenv
from requests import RequestException
from telegram.error import TelegramError

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}


HOMEWORK_STATUSES = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}


logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s, %(levelname)s, %(message)s, %(name)s",
)
logger.addHandler(logging.StreamHandler())


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(f"Удачная отправка сообщения в Telegram: {message}")
    except TelegramError as error:
        logger.error(f"Cбой при отправке сообщения в Telegram: {error}")
        raise TelegramError(
            f"Cбой при отправке сообщения в Telegram: {message}"
        )


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса и возвращает ответ."""
    """Преобразовав его к типам данных Python."""
    timestamp = current_timestamp or int(time.time())
    params = {"from_date": timestamp}
    try:
        homework_status = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
        if homework_status.status_code != HTTPStatus.OK:
            logger.error("Недоступность эндпоинта")
            raise Exception("Недоступность эндпоинта")
    except RequestException:
        logger.error("Cбой при запросе к эндпоинту")
        raise RequestException("Cбой при запросе к эндпоинту")
    try:
        return homework_status.json()
    except JSONDecodeError:
        logger.error("Ответ не преобразован в JSON")
        raise JSONDecodeError("Ответ не преобразован в JSON")


def check_response(response):
    """Проверяет ответ API на корректность."""
    try:
        homework = response["homeworks"]
    except KeyError as error:
        logger.error(f"Отсутствие ожидаемых ключей в ответе API: {error}")
        raise KeyError("Отсутствие ожидаемых ключей в ответе API:")
    if not isinstance(response["homeworks"], list):
        raise TypeError("Неверный тип ответа API")
    return homework


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе ее статус."""
    if ("homework_name") not in homework:
        raise KeyError("Отсутствует ключ homework_name в ответе API")
    if ("status") not in homework:
        raise KeyError("Отсутствует ключ status в ответе API")
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    if homework_status not in HOMEWORK_STATUSES:
        raise KeyError("Такого статуса нет")
    else:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical("Отсутствуют переменные окружения!")
        raise SystemExit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if not homework:
                logger.info("Oтсутствие в ответе новых статусов")
            else:
                send_message(bot, parse_status(homework[0]))
            current_timestamp = response["current_date"]
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logger.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Выход из программы")
        sys.exit(0)
