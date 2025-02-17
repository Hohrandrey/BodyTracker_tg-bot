from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Токен вашего бота
BOT_TOKEN = '7748084790:AAEa0bomHqTJCpLD9cR1ez9K6vtsPxhsNoQ'

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем inline-клавиатуру
    keyboard = [
        [InlineKeyboardButton("Расчёт индекса массы тела", callback_data='rach')],
        [InlineKeyboardButton("Статистика похудения", callback_data='stat')],
        [InlineKeyboardButton("Расчёт калорий на день", callback_data='kkal')],
        [InlineKeyboardButton("Контроль питания", callback_data='control')],
        [InlineKeyboardButton("Напоминания попить воды", callback_data='drink')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопками
    await update.message.reply_text(
        "Привет! Как я могу помочь?\nВыберите один из вариантов",
        reply_markup=reply_markup
    )

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Ответим на callback, чтобы убрать "часики" на кнопке

    if query.data == 'rach':
        await query.edit_message_text(text="Вы выбрали: Рассчитать индекс массы тела")
    elif query.data == 'stat':
        await query.edit_message_text(text="Вы выбрали: Посмотреть статистику похудения")
    elif query.data == 'kkal':
        await query.edit_message_text(text="Вы выбрали: Рассчитать калории на день")
    elif query.data == 'control':
        await query.edit_message_text(text="Вы выбрали: Контроль питания")
    elif query.data == 'drink':#Изменить логику 100%
        await query.edit_message_text(text="Вы выбрали: Попыть")

# Основная функция
if __name__ == '__main__':
    print("Запуск бота...")
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start))

    # Регистрация обработчика нажатий на кнопки
    app.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    print("Бот работает...")
    app.run_polling()