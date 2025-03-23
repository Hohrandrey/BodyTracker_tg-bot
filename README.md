# BodyTracker Telegram Bot

BodyTracker_tg-bot - это Telegram-бот, предназначенный для помощи при похудении.

## Описание
Бот позволяет пользователям:
- Рассчитывать индекс массы тела
- Просматривать статистику похудения
- Расчитывать калории на день
- Контролировать питание
- Устанавливать напоминание о необходимости попить воды

## Зависимости
Проект использует следующие библиотеки Python:
- `python-telegram-bot` - для взаимодействия с Telegram API.
- `python-dotenv` - для работы с переменными окружения.

Полный список зависимостей указан в файле `requirements.txt`.

## Установка и запуск
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Hohrandrey/BodyTracker_tg-bot
   cd BodyTracker_tg-bot
   ```
   
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите бота:
   ```bash
   python BodyTracker_tg-bot.py
   ```