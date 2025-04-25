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
    query = update.callback_query
    # Клавиатура с выбором типа приёма пищи
    keyboard = [
        [InlineKeyboardButton("Завтрак", callback_data="breakfast"),
         InlineKeyboardButton("Обед", callback_data="lunch")],
        [InlineKeyboardButton("Ужин", callback_data="dinner"),
         InlineKeyboardButton("Перекус", callback_data="snack")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите приём пищи:", reply_markup=reply_markup)
    await query.answer()

async def meal_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор типа приёма пищи и запрашивает список продуктов.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция сохраняет выбранный тип приёма пищи и отправляет запрос на ввод продуктов.
    """
    query = update.callback_query
    context.user_data['meal'] = query.data
    await query.message.reply_text(f"Вы выбрали {query.data}. Теперь отправьте список продуктов, которые съели.")
    await query.answer()

async def save_meal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет данные о приёме пищи в базу данных и возвращает пользователя в главное меню.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий текст сообщения.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция сохраняет приём пищи в базу данных и отправляет подтверждение или ошибку.
    """
    user_id = update.message.from_user.id
    date = update.message.date.strftime("%Y-%m-%d")
    meal = context.user_data.get('meal')
    food = update.message.text

    if meal:
        conn = sqlite3.connect("meals.db", check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO meals (user_id, date, meal, food) VALUES (?, ?, ?, ?)", (user_id, date, meal, food))
        conn.commit()
        conn.close()
        await update.message.reply_text("Приём пищи сохранён!")
    else:
        await update.message.reply_text("Сначала выберите приём пищи.")

async def view_meals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатие кнопки 'Просмотреть приёмы пищи' и показывает список по дате.

    Args:
        update (telegram.Update): Объект обновления.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст пользователя.

    Returns:
        None
    """
    query = update.callback_query
    user_id = query.from_user.id

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
