from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application
from datetime import time, datetime
import asyncio

# Состояния для управления напоминаниями
REMINDERS_ON = "reminders_on"
REMINDERS_OFF = "reminders_off"

async def show_reminders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображает меню управления напоминаниями с кнопками включения/выключения, добавления, удаления и возврата.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий информацию о запросе.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция отправляет или редактирует сообщение с меню напоминаний.
    """
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
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
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

async def toggle_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переключает состояние напоминаний (вкл/выкл) и запускает/останавливает задачу уведомлений.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция обновляет состояние и отображает меню напоминаний.
    """
    query = update.callback_query
    await query.answer()

    # Получаем текущее состояние напоминаний
    reminders_state = context.user_data.get('reminders_state', REMINDERS_OFF)

    # Меняем состояние
    if reminders_state == REMINDERS_OFF:
        context.user_data['reminders_state'] = REMINDERS_ON
        await start_reminder_task(context)
    else:
        context.user_data['reminders_state'] = REMINDERS_OFF
        await stop_reminder_task(context)

    # Показываем обновленное меню
    await show_reminders_menu(update, context)

async def add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрашивает у пользователя время для нового напоминания.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция отправляет запрос на ввод времени и устанавливает состояние ожидания.
    """
    query = update.callback_query
    await query.answer()

    # Запрашиваем время для нового напоминания
    await query.edit_message_text(text="Введите время для нового напоминания в формате ЧЧ:ММ (например, 09:30):")
    context.user_data['state'] = 'waiting_for_reminder_time'

async def handle_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает введённое пользователем время для напоминания и сохраняет его.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий текст сообщения.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция сохраняет напоминание и возвращает пользователя в меню.

    Raises:
        ValueError: Если формат времени некорректен (обрабатывается внутри функции).
        IndexError: Если строка времени не содержит разделителя ':' (обрабатывается внутри функции).
    """
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
        context.user_data['reminders'].sort()

        await update.message.reply_text(f"Напоминание добавлено на {time_str}.")
        await show_reminders_menu(update, context)
    except (ValueError, IndexError):
        await update.message.reply_text("Некорректный формат времени. Введите время в формате ЧЧ:ММ (например, 09:30).")

async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображает список напоминаний для выбора удаления или сообщение об их отсутствии.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция отправляет список напоминаний или сообщение об их отсутствии.
    """
    query = update.callback_query
    await query.answer()

    # Проверяем, есть ли напоминания
    if 'reminders' not in context.user_data or not context.user_data['reminders']:
        await query.message.reply_text("Нет активных напоминаний.")
        await show_reminders_menu(update, context)
        return

    # Создаем клавиатуру для выбора напоминания для удаления
    keyboard = [
        [InlineKeyboardButton(f"{t.strftime('%H:%M')}", callback_data=f"delete_{t.strftime('%H:%M')}")]
        for t in context.user_data['reminders']
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='back_to_reminders')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Выберите напоминание для удаления:",
        reply_markup=reply_markup
    )

async def handle_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет выбранное пользователем напоминание.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция удаляет напоминание и возвращает пользователя в меню.
    """
    query = update.callback_query
    await query.answer()

    # Извлекаем время из callback_data
    time_to_delete = query.data.split("_")[1]

    # Удаляем напоминание
    reminders = context.user_data.get('reminders', [])
    reminders = [t for t in reminders if t.strftime('%H:%M') != time_to_delete]
    context.user_data['reminders'] = reminders

    await query.edit_message_text(text=f"Напоминание на {time_to_delete} удалено.")
    await show_reminders_menu(update, context)

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, start_func):
    """Возвращает пользователя в главное меню.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий информацию о запросе.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.
        start_func (callable): Функция для отображения главного меню.

    Returns:
        None: Функция вызывает start_func для возврата в главное меню.
    """
    query = update.callback_query
    await query.answer()

    # Сохраняем chat_id для уведомлений
    if update.message:
        context.user_data['chat_id'] = update.message.chat_id
    elif update.callback_query:
        context.user_data['chat_id'] = update.callback_query.message.chat_id

    # Возвращаемся в главное меню
    await start_func(update, context)

async def back_to_reminders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возвращает пользователя в меню напоминаний.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция вызывает show_reminders_menu для возврата в меню напоминаний.
    """
    query = update.callback_query
    await query.answer()

    # Возвращаемся в меню напоминаний
    await show_reminders_menu(update, context)

async def start_reminder_task(context: ContextTypes.DEFAULT_TYPE):
    """Запускает задачу для периодической проверки и отправки напоминаний.

    Args:
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция создаёт задачу asyncio для отправки уведомлений.
    """
    if 'reminder_task' not in context.user_data or context.user_data['reminder_task'].done():
        context.user_data['reminder_task'] = asyncio.create_task(send_reminders(context))

async def stop_reminder_task(context: ContextTypes.DEFAULT_TYPE):
    """Останавливает задачу уведомлений, если она запущена.

    Args:
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция отменяет задачу и удаляет её из контекста.
    """
    if 'reminder_task' in context.user_data:
        context.user_data['reminder_task'].cancel()
        del context.user_data['reminder_task']

async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Периодически проверяет время и отправляет напоминания пользователю.

    Args:
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция работает в бесконечном цикле, отправляя уведомления по расписанию.
    """
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