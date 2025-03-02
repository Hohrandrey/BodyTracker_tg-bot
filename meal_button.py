from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import sqlite3


def get_meal_button():
    keyboard = [[InlineKeyboardButton("Добавить приём пищи", callback_data="add_meal")]]
    return InlineKeyboardMarkup(keyboard)


def meal_button_handler(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    date = query.message.date.strftime("%Y-%m-%d")

    conn = sqlite3.connect("meals.db", check_same_thread=False)
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS meals (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, meal TEXT, food TEXT)''')
    conn.commit()

    keyboard = [[InlineKeyboardButton("Завтрак", callback_data="breakfast"),
                 InlineKeyboardButton("Обед", callback_data="lunch")],
                [InlineKeyboardButton("Ужин", callback_data="dinner"),
                 InlineKeyboardButton("Перекус", callback_data="snack")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text("Выберите приём пищи:", reply_markup=reply_markup)
    query.answer()


def meal_choice_handler(update, context):
    query = update.callback_query
    context.user_data['meal'] = query.data
    query.message.reply_text(f"Вы выбрали {query.data}. Теперь отправьте список продуктов, которые съели.")
    query.answer()


def save_meal(update, context):
    user_id = update.message.from_user.id
    date = update.message.date.strftime("%Y-%m-%d")
    meal = context.user_data.get('meal')
    food = update.message.text

    if meal:
        conn = sqlite3.connect("meals.db", check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO meals (user_id, date, meal, food) VALUES (?, ?, ?, ?)", (user_id, date, meal, food))
        conn.commit()
        update.message.reply_text("Приём пищи сохранён!")
    else:
        update.message.reply_text("Сначала выберите приём пищи.")


def get_meal_button_handler():
    return CallbackQueryHandler(meal_button_handler, pattern='^add_meal$')


def get_meal_choice_handler():
    return CallbackQueryHandler(meal_choice_handler, pattern='^(breakfast|lunch|dinner|snack)$')
