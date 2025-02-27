from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application
from datetime import time, datetime
import asyncio

# Состояния для управления напоминаниями
REMINDERS_ON = "reminders_on"
REMINDERS_OFF = "reminders_off"

# Функция для отображения меню напоминаний
async def show_reminders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем текущее состояние напоминаний
    reminders_state = context.user_data.get('reminders_state', REMINDERS_OFF)

    # Создаем inline-клавиатуру с кнопками
    keyboard = [
        [InlineKeyboardButton(
            "✅ Включить напоминания" if reminders_state == REMINDERS_OFF else "❌ Выключить напоминания",
            callback_data='toggle_reminders'
        )],
        [InlineKeyboardButton("➕ Добавить напоминание", callback_data='add_reminder')],
        [InlineKeyboardButton("➖ Удалить напоминание", callback_data='delete_reminder')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]  # Возврат в главное меню
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Проверяем, откуда пришел запрос (из callback или message)
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text="Управление напоминаниями:",
            reply_markup=reply_markup
        )
    elif update.message:
        await update.message.reply_text(
            text="Управление напоминаниями:",
            reply_markup=reply_markup
        )

# Функция для включения/выключения напоминаний
async def toggle_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Получаем текущее состояние напоминаний
    reminders_state = context.user_data.get('reminders_state', REMINDERS_OFF)

    # Меняем состояние
    if reminders_state == REMINDERS_OFF:
        context.user_data['reminders_state'] = REMINDERS_ON
        await start_reminder_task(context)  # Запускаем задачу для уведомлений
    else:
        context.user_data['reminders_state'] = REMINDERS_OFF
        await stop_reminder_task(context)  # Останавливаем задачу для уведомлений

    # Показываем обновленное меню
    await show_reminders_menu(update, context)

# Функция для добавления напоминания
async def add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Запрашиваем время для нового напоминания
    await query.edit_message_text(text="Введите время для нового напоминания в формате ЧЧ:ММ (например, 09:30):")
    context.user_data['state'] = 'waiting_for_reminder_time'

# Функция для обработки ввода времени напоминания
async def handle_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Парсим введенное время
        time_str = update.message.text
        hours, minutes = map(int, time_str.split(':'))
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            await update.message.reply_text("Некорректное время. Введите время в формате ЧЧ:ММ (например, 09:30).")
            return

        # Сохраняем напоминание
        if 'reminders' not in context.user_data:
            context.user_data['reminders'] = []
        context.user_data['reminders'].append(time(hours, minutes))
        context.user_data['reminders'].sort()  # Сортируем для удобства

        await update.message.reply_text(f"Напоминание добавлено на {time_str}.")
        await show_reminders_menu(update, context)  # Возвращаемся в меню напоминаний
    except (ValueError, IndexError):
        await update.message.reply_text("Некорректный формат времени. Введите время в формате ЧЧ:ММ (например, 09:30).")

# Функция для удаления напоминания
async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Проверяем, есть ли напоминания
    if 'reminders' not in context.user_data or not context.user_data['reminders']:
        # Отправляем отдельное сообщение, если напоминаний нет
        await query.message.reply_text("Нет активных напоминаний.")
        await show_reminders_menu(update, context)  # Возвращаемся в меню напоминаний
        return

    # Создаем клавиатуру для выбора напоминания для удаления
    keyboard = [
        [InlineKeyboardButton(f"{t.strftime('%H:%M')}", callback_data=f"delete_{t.strftime('%H:%M')}")]
        for t in context.user_data['reminders']
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='back_to_reminders')])  # Возврат в меню напоминаний
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Выберите напоминание для удаления:",
        reply_markup=reply_markup
    )

# Функция для обработки удаления напоминания
async def handle_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Извлекаем время из callback_data
    time_to_delete = query.data.split("_")[1]

    # Удаляем напоминание
    reminders = context.user_data.get('reminders', [])
    reminders = [t for t in reminders if t.strftime('%H:%M') != time_to_delete]
    context.user_data['reminders'] = reminders

    await query.edit_message_text(text=f"Напоминание на {time_to_delete} удалено.")
    await show_reminders_menu(update, context)  # Возвращаемся в меню напоминаний

# Функция для возврата в главное меню
async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, start_func):
    query = update.callback_query
    await query.answer()

    # Сохраняем chat_id для уведомлений
    if update.message:
        context.user_data['chat_id'] = update.message.chat_id
    elif update.callback_query:
        context.user_data['chat_id'] = update.callback_query.message.chat_id

    # Возвращаемся в главное меню
    await start_func(update, context)

# Функция для возврата в меню напоминаний
async def back_to_reminders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Возвращаемся в меню напоминаний
    await show_reminders_menu(update, context)

# Функция для запуска задачи уведомлений
async def start_reminder_task(context: ContextTypes.DEFAULT_TYPE):
    if 'reminder_task' not in context.user_data or context.user_data['reminder_task'].done():
        context.user_data['reminder_task'] = asyncio.create_task(send_reminders(context))

# Функция для остановки задачи уведомлений
async def stop_reminder_task(context: ContextTypes.DEFAULT_TYPE):
    if 'reminder_task' in context.user_data:
        context.user_data['reminder_task'].cancel()
        del context.user_data['reminder_task']

# Функция для отправки уведомлений
async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    while True:
        now = datetime.now().time()
        reminders = context.user_data.get('reminders', [])
        for reminder_time in reminders:
            if now.hour == reminder_time.hour and now.minute == reminder_time.minute:
                await context.bot.send_message(
                    chat_id=context.user_data['chat_id'],
                    text="⏰ Пора попить воды! 💧"
                )
                await asyncio.sleep(60)  # Ждем минуту, чтобы не отправлять уведомление несколько раз
        await asyncio.sleep(30)  # Проверяем время каждые 30 секунд