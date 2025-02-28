from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def handle_calories_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Мужской", callback_data='gender_m')],
        [InlineKeyboardButton("Женский", callback_data='gender_f')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text="Вы выбрали: Рассчитать калории на день\nВыберите ваш пол:",
        reply_markup=reply_markup
    )
    context.user_data['state'] = 'waiting_for_gender'


async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    gender = 'м' if query.data == 'gender_m' else 'ж'
    context.user_data['gender'] = gender

    await query.edit_message_text(text="Введите ваш возраст:")
    context.user_data['state'] = 'waiting_for_age'


async def handle_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text)
        if not 1 <= age <= 120:
            raise ValueError
        context.user_data['age'] = age
        await update.message.reply_text("Введите ваш вес в кг:")
        context.user_data['state'] = 'waiting_for_calories_weight'
    except:
        await update.message.reply_text("Некорректный возраст. Введите число от 1 до 120:")


async def handle_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text.replace(',', '.'))
        if weight <= 0:
            raise ValueError
        context.user_data['weight'] = weight
        await update.message.reply_text("Введите ваш рост в см:")
        context.user_data['state'] = 'waiting_for_calories_height'
    except:
        await update.message.reply_text("Некорректный вес. Введите положительное число:")


async def handle_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = float(update.message.text.replace(',', '.'))
        if height <= 0:
            raise ValueError
        context.user_data['height'] = height

        keyboard = [
            [InlineKeyboardButton("Сидячий образ жизни", callback_data='activity_1')],
            [InlineKeyboardButton("Легкая активность", callback_data='activity_2')],
            [InlineKeyboardButton("Умеренная активность", callback_data='activity_3')],
            [InlineKeyboardButton("Высокая активность", callback_data='activity_4')],
            [InlineKeyboardButton("Экстремальная активность", callback_data='activity_5')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Выберите уровень физической активности:",
            reply_markup=reply_markup
        )
        context.user_data['state'] = 'waiting_for_activity'
    except:
        await update.message.reply_text("Некорректный рост. Введите положительное число:")


async def handle_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    activity_level = int(query.data.split('_')[1])
    context.user_data['activity'] = activity_level

    user_data = context.user_data
    calories = calculate_calories(
        gender=user_data['gender'],
        weight=user_data['weight'],
        height=user_data['height'],
        age=user_data['age'],
        activity_level=activity_level
    )

    await query.edit_message_text(
        text=f"Ваша суточная норма калорий: {calories:.0f} ккал\n"
             "Для возврата в меню нажмите /start"
    )
    context.user_data.clear()


def calculate_calories(gender: str, weight: float, height: float, age: int, activity_level: int) -> float:
    # Формула Миффлина-Сан Жеора
    if gender == 'м':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_multipliers = {
        1: 1.2,  # Минимальная активность
        2: 1.375,  # Легкая активность
        3: 1.55,  # Умеренная активность
        4: 1.725,  # Высокая активность
        5: 1.9  # Экстремальная активность
    }

    return bmr * activity_multipliers.get(activity_level, 1.2)