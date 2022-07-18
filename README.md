# homework_bot
python telegram bot
# homework_bot

## Оглавление
- [Описание](#description)
- [Технологии](#technologies)
- [Запуск проекта](#launch)

<a id=description></a>
## Описание
Телеграмм-бот, созданный для контроля статуса проверки домашнего задания студента Яндекс.Практикума. Обращается к API сервиса Практикум.Домашка, узнает статус домашней работы, в случае изменений отправляет уведомление. Проект выполнен в рамках получения практических навыков по работе с API, исключениями и логированием.

<a id=technologies></a>
## Технологии
- Python 3.10
- python-dotenv 
- python-telegram-bot
- Simple JWT

<a id=launch></a>
## Запуск проекта:
### Клонировать репозиторий:
```bash
git clone git@github.com:V-pix/homework_bot

```
### Перейти в репозиторий в командной строке:
```bash
cd homework_bot
```
### Cоздать виртуальное окружение:
```bash
python -m venv venv
```
### Активировать виртуальное окружение:
```bash
source venv/bin/activate        # для Linux
source venv/Scripts/activate    # для Windows
```
### Установить зависимости из файла requirements.txt:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
### Записать в переменные окружения (файл .env) необходимые ключи:
```bash
PRACTICUM_TOKEN=<Ваш токен Яндекс.Практикума>
TELEGRAM_TOKEN=<Токен телеграмм-бота>
TELEGRAM_CHAT_ID=<ваш id в Телеграмме>
```
### Запустить файл homework.py
