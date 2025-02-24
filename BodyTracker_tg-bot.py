from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from bmi_calculator import handle_weight, handle_height  # Импортируем функции из bmi_calculator.py
from water_reminder import set_water_reminder, handle_interval  # Импортируем функции из water_reminder.py

# Токен вашего бота
BOT_TOKEN = '7748084790:AAEa0bomHqTJCpLD9cR1ez9K6vtsPxhsNoQ'

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Рассчитать индекс массы тела", callback_data='rach')],
        [InlineKeyboardButton("Статистика похудения", callback_data='stat')],
        [InlineKeyboardButton("Рассчитать калории на день", callback_data='kkal')],
        [InlineKeyboardButton("Контроль питания", callback_data='control')],
        [InlineKeyboardButton("Напоминания попить воды", callback_data='drink')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Как я могу помочь?\nВыберите один из вариантов:",
        reply_markup=reply_markup
    )

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'rach':
        await query.edit_message_text(text="Вы выбрали: Рассчитать индекс массы тела")
        await query.message.reply_text("Введите ваш вес в килограммах (например, 70):")
        context.user_data['state'] = 'waiting_for_weight'
    elif query.data == 'stat':
        await query.edit_message_text(text="Вы выбрали: Посмотреть статистику похудения")
    elif query.data == 'kkal':
        await query.edit_message_text(text="Вы выбрали: Рассчитать калории на день")
    elif query.data == 'control':
        await query.edit_message_text(text="Вы выбрали: Контроль питания")
    elif query.data == 'drink':
        await set_water_reminder(update, context)

# Обработка сообщений от пользователя
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state', None)
    if state == 'waiting_for_weight':
        await handle_weight(update, context)  # Используем функцию из bmi_calculator.py
    elif state == 'waiting_for_height':
        await handle_height(update, context)  # Используем функцию из bmi_calculator.py
    elif state == 'waiting_for_interval':
        await handle_interval(update, context)  # Используем функцию из water_reminder.py

# Основная функция
if __name__ == '__main__':
    print("Запуск бота...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Бот работает...")
    app.run_polling()