# Используем официальный образ Python как базовый
FROM python:3.9-slim
# Устанавливаем рабочую директорию в контейнере
WORKDIR /app
# Копируем файлы зависимостей
COPY requirements.txt .
# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Копируем весь код проекта
COPY . .
# Указываем команду для запуска приложения
CMD ["python", "BodyTracker_tg-bot.py"]