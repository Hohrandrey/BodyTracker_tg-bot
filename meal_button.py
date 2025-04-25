from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes
import sqlite3

async def meal_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатие кнопки 'Добавить приём пищи' и отображает меню выбора типа приёма пищи.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция отправляет сообщение с выбором типа приёма пищи.
    """
    """Обрабатывает нажатие кнопки 'Добавить приём пищи' и отображает меню выбора типа приёма пищи."""
    query = update.callback_query
    user_id = query.from_user.id
    date = query.message.date.strftime("%Y-%m-%d")

    # Подключение к базе данных и создание таблицы, если её нет
    conn = sqlite3.connect("meals.db", check_same_thread=False)
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS meals (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, meal TEXT, food TEXT)''')
    conn.commit()
    conn.close()

    # Клавиатура с выбором типа приёма пищи
    keyboard = [[InlineKeyboardButton("Завтрак", callback_data="breakfast"),
                 InlineKeyboardButton("Обед", callback_data="lunch")],
                [InlineKeyboardButton("Ужин", callback_data="dinner"),
                 InlineKeyboardButton("Перекус", callback_data="snack")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите приём пищи:", reply_markup=reply_markup)
    await query.answer()


# Обработчик для выбора типа приёма пищи
async def meal_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор типа приёма пищи и запрашивает список продуктов."""
    query = update.callback_query
    context.user_data['meal'] = query.data
    await query.message.reply_text(f"Вы выбрали {query.data}. Теперь отправьте список продуктов, которые съели.")
    await query.answer()


# Сохраняем приём пищи в базу данных
async def save_meal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет данные о приёме пищи в базу данных и возвращает пользователя в главное меню."""
    user_id = update.message.from_user.id
    date = update.message.date.strftime("%Y-%m-%d")
    meal = context.user_data.get('meal')  # Получаем тип приёма пищи
    food = update.message.text  # Получаем список продуктов

    if meal:  # Проверяем, был ли выбран приём пищи
        # Подключаемся к базе данных и сохраняем информацию
        conn = sqlite3.connect("meals.db", check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO meals (user_id, date, meal, food) VALUES (?, ?, ?, ?)", (user_id, date, meal, food))
        conn.commit()
        conn.close()
        await update.message.reply_text("Приём пищи сохранён!")
    else:
        await update.message.reply_text("Сначала выберите приём пищи.")


# Обработчик для просмотра сохранённых приёмов пищи
async def view_meals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатие кнопки 'Просмотреть приёмы пищи' и показывает список по дате."""
    query = update.callback_query
    user_id = query.from_user.id

    # Подключаемся к базе данных
    conn = sqlite3.connect("meals.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT date, meal, food FROM meals WHERE user_id = ? ORDER BY date DESC", (user_id,))
    meals = c.fetchall()
    conn.close()

    if meals:
        message = "Ваши приёмы пищи:\n\n"
        for date, meal, food in meals:
            message += f"📅 *{date}* — 🍽️ *{meal}*\n{food}\n\n"
    else:
        message = "У вас пока нет сохранённых приёмов пищи."

    await query.message.reply_text(message, parse_mode='Markdown')
    await query.answer()

