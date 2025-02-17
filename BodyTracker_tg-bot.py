from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Токен вашего бота
BOT_TOKEN = '7748084790:AAEa0bomHqTJCpLD9cR1ez9K6vtsPxhsNoQ'

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем inline-клавиатуру
    keyboard = [
        [InlineKeyboardButton("Рассчитать индекс массы тела", callback_data='rach')],
        [InlineKeyboardButton("Статистика похудения", callback_data='stat')],
        [InlineKeyboardButton("Рассчитать калории на день", callback_data='kkal')],
        [InlineKeyboardButton("Контроль питания", callback_data='control')],
        [InlineKeyboardButton("Напоминания попить воды", callback_data='drink')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопками
    await update.message.reply_text(
        "Привет! Как я могу помочь?\nВыберите один из вариантов:",
        reply_markup=reply_markup
    )

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Ответим на callback, чтобы убрать "часики" на кнопке

    if query.data == 'rach':
        await query.edit_message_text(text="Вы выбрали: Рассчитать индекс массы тела")
        await query.message.reply_text("Введите ваш вес в килограммах (например, 70):")
        context.user_data['state'] = 'waiting_for_weight'  # Устанавливаем состояние ожидания веса
    elif query.data == 'stat':
        await query.edit_message_text(text="Вы выбрали: Посмотреть статистику похудения")
    elif query.data == 'kkal':
        await query.edit_message_text(text="Вы выбрали: Рассчитать калории на день")
    elif query.data == 'control':
        await query.edit_message_text(text="Вы выбрали: Контроль питания")
    elif query.data == 'drink':
        await query.edit_message_text(text="Вы выбрали: Напоминание попить воды")

# Обработка сообщений от пользователя
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state', None)
    if state == 'waiting_for_weight':
        await handle_weight(update, context)
    elif state == 'waiting_for_height':
        await handle_height(update, context)

# Функция для обработки ввода веса
async def handle_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text)
        if weight <= 0:
            await update.message.reply_text("Вес должен быть положительным числом. Попробуйте снова.")
            return
        context.user_data['weight'] = weight
        await update.message.reply_text("Введите ваш рост в сантиметрах (например, 175):")
        context.user_data['state'] = 'waiting_for_height'  # Устанавливаем состояние ожидания роста
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для веса.")

# Функция для обработки ввода роста
async def handle_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = float(update.message.text)
        if height <= 0:
            await update.message.reply_text("Рост должен быть положительным числом. Попробуйте снова.")
            return
        context.user_data['height'] = height

        # Получаем вес и рост из контекста
        weight = context.user_data['weight']
        height = context.user_data['height'] / 100  # Переводим рост в метры

        # Рассчитываем ИМТ
        bmi = weight / (height ** 2)
        bmi = round(bmi, 2)  # Округляем до двух знаков после запятой

        # Определяем категорию ИМТ
        if bmi < 18.5:
            category = "Недостаточный вес"
        elif 18.5 <= bmi < 24.9:
            category = "Нормальный вес"
        elif 25 <= bmi < 29.9:
            category = "Избыточный вес"
        else:
            category = "Ожирение"

        # Отправляем результат пользователю
        await update.message.reply_text(
            f"Ваш индекс массы тела (ИМТ): {bmi}\n"
            f"Категория: {category}"
        )
        await start(update, context)
        context.user_data['state'] = None  # Сбрасываем состояние
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для роста.")
        context.user_data['state'] = None  # Сбрасываем состояние
# Основная функция
if __name__ == '__main__':
    print("Запуск бота...")
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start))

    # Регистрация обработчика нажатий на кнопки
    app.add_handler(CallbackQueryHandler(button_handler))

    # Регистрация обработчика текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Запуск бота
    print("Бот работает...")
    app.run_polling()