from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен вашего бота
BOT_TOKEN = '7748084790:AAEa0bomHqTJCpLD9cR1ez9K6vtsPxhsNoQ'

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем клавиатуру с кнопками
    keyboard = [
        ["Индекс массы тела"],
        ["Статистика похудения"],
        ["Расчёт калорий на день"],
        ["Контроль питания"],
        ["Напоминания попить воды"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Я ваш бот. Как я могу помочь?", reply_markup=reply_markup)

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Индекс массы тела":
        await update.message.reply_text("Вы выбрали: Индекс массы тела")
    elif text == "Статистика похудения":
        await update.message.reply_text("Вы выбрали: Статистика похудения")
    elif text == "Расчёт калорий на день":
        await update.message.reply_text("Вы выбрали: Расчёт калорий на день")
    elif text == "Контроль питания":
        await update.message.reply_text("Вы выбрали: Контроль питания")
    elif text == "Напоминания попить воды":
        await update.message.reply_text("Вы выбрали: Напоминания попить воды")
    else:
        await update.message.reply_text(f"Вы написали: {text}")

# Обработчик ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")

# Основная функция
if __name__ == '__main__':
    print("Запуск бота...")
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start))

    # Регистрация обработчиков текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Регистрация обработчика ошибок
    app.add_error_handler(error)

    # Запуск бота
    print("Бот работает...")
    app.run_polling()