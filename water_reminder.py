from telegram import Update
from telegram.ext import ContextTypes, Application
import asyncio

# Функция для установки напоминания
async def set_water_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(text="Вы выбрали: Напоминание попить воды")
    await update.callback_query.message.reply_text("Введите интервал напоминаний в минутах (например, 30):")
    context.user_data['state'] = 'waiting_for_interval'

# Функция для обработки ввода интервала
async def handle_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        interval = int(update.message.text)
        if interval <= 0:
            await update.message.reply_text("Интервал должен быть положительным числом. Попробуйте снова.")
            return
        context.user_data['interval'] = interval
        await update.message.reply_text(f"Напоминания будут приходить каждые {interval} минут.")
        await start_reminders(update, context)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для интервала.")

# Функция для запуска напоминаний
async def start_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    interval = context.user_data['interval']
    chat_id = update.message.chat_id
    while True:
        await asyncio.sleep(interval * 60)  # Переводим минуты в секунды
        await context.bot.send_message(chat_id=chat_id, text="⏰ Пора попить воды! 💧")

# Функция для остановки напоминаний (опционально)
async def stop_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'reminder_task' in context.user_data:
        context.user_data['reminder_task'].cancel()
        await update.message.reply_text("Напоминания остановлены.")
    else:
        await update.message.reply_text("Напоминания не были запущены.")