from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from bmi_calculator import handle_weight, handle_height
from water_reminder import (
    show_reminders_menu, toggle_reminders, add_reminder, handle_reminder_time,
    delete_reminder, handle_delete_reminder, back_to_main_menu, back_to_reminders_menu
)
from weight_statistics import (
    show_weight_statistics_menu, enter_weight, handle_weight_stat, back_to_main_menu_from_stat
)
from CaloriesCalculator import (
    handle_calories_start, handle_gender, handle_age, handle_weigh, handle_heigh, handle_activity
)
from meal_button import meal_button_handler, meal_choice_handler,back_to_main_menu, save_meal, view_meals_handler

# Токен вашего бота
BOT_TOKEN = '7748084790:AAEa0bomHqTJCpLD9cR1ez9K6vtsPxhsNoQ'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображает главное меню бота с основными функциями.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий сообщение или callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция отправляет сообщение с меню в чат и сохраняет chat_id пользователя.
    """
    keyboard = [
        [InlineKeyboardButton("Рассчитать индекс массы тела", callback_data='rach')],
        [InlineKeyboardButton("Статистика похудения", callback_data='stat')],
        [InlineKeyboardButton("Рассчитать калории на день", callback_data='kkal')],
        [InlineKeyboardButton("Контроль питания", callback_data='control')],
        [InlineKeyboardButton("Напоминания попить воды", callback_data='reminders')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Сохраняем chat_id для уведомлений
    if update.message:
        context.user_data['chat_id'] = update.message.chat_id
    elif update.callback_query:
        context.user_data['chat_id'] = update.callback_query.message.chat_id

    # Проверяем, откуда пришел запрос (из команды или callback)
    if update.message:
        await update.message.reply_text(
            "Привет! Как я могу помочь?\nВыберите один из вариантов:",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Привет! Как я могу помочь?\nВыберите один из вариантов:",
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на кнопки в меню и вызывает соответствующие функции.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция перенаправляет запрос на соответствующую обработку в зависимости от callback_data.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'rach':
        await query.edit_message_text(text="Вы выбрали: Рассчитать индекс массы тела")
        await query.message.reply_text("Введите ваш вес в килограммах (например, 70):")
        context.user_data['state'] = 'waiting_for_weight'
    elif query.data == 'stat':
        await show_weight_statistics_menu(update, context)
    elif query.data == 'enter_weight':
        await enter_weight(update, context)
    elif query.data == 'kkal':
        await handle_calories_start(update, context)
    elif query.data == 'control':
        # Показываем меню с "Добавить приём пищи" и "Просмотреть приёмы пищи"
        keyboard = [
            [InlineKeyboardButton("Добавить приём пищи", callback_data="add_meal")],
            [InlineKeyboardButton("Просмотреть приёмы пищи", callback_data="view_meals")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите действие:", reply_markup=reply_markup)
    elif query.data == 'add_meal':
        await meal_button_handler(update, context)
    elif query.data == 'view_meals':
        await view_meals_handler(update, context)
    elif query.data == 'reminders':
        await toggle_reminders(update, context)
    elif query.data == 'add_reminder':
        await add_reminder(update, context)
    elif query.data == 'delete_reminder':
        await delete_reminder(update, context)
    elif query.data.startswith('delete_'):
        await handle_delete_reminder(update, context)
    elif query.data == 'back_to_main':
        await back_to_main_menu_from_stat(update, context, start)
    elif query.data == 'back_to_main':  # Добавляем новое условие для возврата в главное меню
        await back_to_main_menu(update, context, start)
    elif query.data == 'back_to_reminders':
        await back_to_reminders_menu(update, context)
    elif query.data in ['gender_m', 'gender_f']:
        await handle_gender(update, context)
    elif query.data.startswith('activity_'):
        await handle_activity(update, context)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения пользователя в зависимости от текущего состояния.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий текст сообщения.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция вызывает соответствующую функцию обработки на основе состояния пользователя.

    Notes:
        Состояние хранится в context.user_data['state'] и определяет, какой ввод ожидается.
    """
    state = context.user_data.get('state', None)
    if state == 'waiting_for_weight':
        await handle_weight(update, context)
    elif state == 'waiting_for_height':
        await handle_height(update, context, start)
    elif state == 'waiting_for_reminder_time':
        await handle_reminder_time(update, context)
    elif state == 'waiting_for_weight_stat':
        await handle_weight_stat(update, context, start)
    elif state == 'waiting_for_age':
        await handle_age(update, context)
    elif state == 'waiting_for_calories_weight':
        await handle_weigh(update, context)
    elif state == 'waiting_for_calories_height':
        await handle_heigh(update, context)
    elif 'meal' in context.user_data:
        # Если пользователь выбрал приём пищи, сохраняем еду
        await save_meal(update, context)
        await back_to_main_menu(update, context, start)

if __name__ == '__main__':
    """Запускает Telegram-бота с заданными обработчиками команд и событий."""
    print("Запуск бота...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(meal_choice_handler, pattern='^(breakfast|lunch|dinner|snack)$'))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))


    print("Бот работает...")
    app.run_polling()