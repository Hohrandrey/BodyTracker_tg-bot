from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio

# Состояния для управления напоминаниями
REMINDERS_ON = "reminders_on"
REMINDERS_OFF = "reminders_off"

# Функция для отображения меню напоминаний
async def show_reminders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем inline-клавиатуру с тремя кнопками
    keyboard = [
        [InlineKeyboardButton("Включить/Выключить напоминания", callback_data='toggle_reminders')],
        [InlineKeyboardButton("Добавить напоминание", callback_data='add_reminder')],
        [InlineKeyboardButton("Удалить напоминание", callback_data='delete_reminder')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопками
    await update.callback_query.edit_message_text(
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
        await query.edit_message_text(text="Напоминания включены.")
    else:
        context.user_data['reminders_state'] = REMINDERS_OFF
        await query.edit_message_text(text="Напоминания выключены.")

    # Показываем меню напоминаний снова
    await show_reminders_menu(update, context)

# Функция для добавления напоминания
async def add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Запрашиваем время для нового напоминания
    await query.edit_message_text(text="Введите время для нового напоминания (например, 9, 15, 23):")
    context.user_data['state'] = 'waiting_for_reminder_time'

# Функция для обработки ввода времени напоминания
async def handle_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        time = int(update.message.text)
        if time < 0 or time > 23:
            await update.message.reply_text("Время должно быть числом от 0 до 23. Попробуйте снова.")
            return

        # Сохраняем напоминание
        if 'reminders' not in context.user_data:
            context.user_data['reminders'] = []
        context.user_data['reminders'].append(time)
        context.user_data['reminders'].sort()  # Сортируем для удобства

        await update.message.reply_text(f"Напоминание добавлено на {time}:00.")
        await show_reminders_menu(update, context)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для времени.")

# Функция для удаления напоминания
async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Проверяем, есть ли напоминания
    if 'reminders' not in context.user_data or not context.user_data['reminders']:
        await query.edit_message_text(text="Нет активных напоминаний.")
        await show_reminders_menu(update, context)
        return

    # Создаем клавиатуру для выбора напоминания для удаления
    keyboard = [
        [InlineKeyboardButton(f"{time}:00", callback_data=f"delete_{time}")]
        for time in context.user_data['reminders']
    ]
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
    time_to_delete = int(query.data.split("_")[1])

    # Удаляем напоминание
    context.user_data['reminders'].remove(time_to_delete)
    await query.edit_message_text(text=f"Напоминание на {time_to_delete}:00 удалено.")
    await show_reminders_menu(update, context)