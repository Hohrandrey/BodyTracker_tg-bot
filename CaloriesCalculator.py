from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_calories_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс расчёта калорий, запрашивая пол пользователя.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция отправляет сообщение с выбором пола и устанавливает состояние ожидания.
    """
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
    print("State set to waiting_for_gender")

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор пола и запрашивает возраст пользователя.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция сохраняет пол, отправляет запрос возраста и обновляет состояние.
    """
    query = update.callback_query
    await query.answer()

    gender = 'м' if query.data == 'gender_m' else 'ж'
    context.user_data['gender'] = gender
    print(f"Gender set to {gender}")

    await query.edit_message_text(text="Введите ваш возраст:")
    context.user_data['state'] = 'waiting_for_age'
    print("State set to waiting_for_age")

async def handle_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает введённый возраст и запрашивает вес пользователя.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий текст сообщения.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция сохраняет возраст, запрашивает вес или отправляет сообщение об ошибке.

    Raises:
        ValueError: Если возраст не является числом или выходит за пределы 1–120 (обрабатывается внутри).
    """
    try:
        age = int(update.message.text)
        if not 1 <= age <= 120:
            raise ValueError
        context.user_data['age'] = age
        await update.message.reply_text("Введите ваш вес в кг:")
        context.user_data['state'] = 'waiting_for_calories_weight'
        print("State set to waiting_for_calories_weight")
    except:
        await update.message.reply_text("Некорректный возраст. Введите число от 1 до 120:")

async def handle_weigh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает введённый вес и запрашивает рост пользователя.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий текст сообщения.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция сохраняет вес, запрашивает рост или отправляет сообщение об ошибке.

    Raises:
        ValueError: Если вес не является числом или не положительный (обрабатывается внутри).
    """
    try:
        weight = float(update.message.text.replace(',', '.'))
        if weight <= 0:
            raise ValueError
        context.user_data['weight'] = weight
        await update.message.reply_text("Введите ваш рост в см:")
        context.user_data['state'] = 'waiting_for_calories_height'
        print("State set to waiting_for_calories_height")
    except:
        await update.message.reply_text("Некорректный вес. Введите положительное число:")

async def handle_heigh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает введённый рост и запрашивает уровень активности пользователя.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий текст сообщения.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция сохраняет рост, отправляет выбор активности или сообщение об ошибке.

    Raises:
        ValueError: Если рост не является числом или не положительный (обрабатывается внутри).
    """
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
        print("State set to waiting_for_activity")
    except:
        await update.message.reply_text("Некорректный рост. Введите положительное число:")

async def handle_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор уровня активности, рассчитывает калории и завершает процесс.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий callback-запрос.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция рассчитывает калории, отправляет результат и очищает данные пользователя.
    """
    query = update.callback_query
    await query.answer()

    activity_level = int(query.data.split('_')[1])
    context.user_data['activity'] = activity_level

    user_data = context.user_data
    print(f"User data before calculation: {user_data}")

    calories = calculate_calories(
        gender=user_data['gender'],
        weight=user_data['weight'],
        height=user_data['height'],
        age=user_data['age'],
        activity_level=activity_level
    )

    # Создаем клавиатуру с кнопкой для возврата в главное меню
    keyboard = [
        [InlineKeyboardButton("Вернуться в главное меню", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=f"Ваша суточная норма калорий: {calories:.0f} ккал\n"
             "Для возврата в меню нажмите кнопку ниже:",
        reply_markup=reply_markup
    )
    context.user_data.clear()
    print("User data cleared")

def calculate_calories(gender: str, weight: float, height: float, age: int, activity_level: int) -> float:
    """Рассчитывает суточную норму калорий по формуле Миффлина-Сан Жеора с учётом активности.

    Args:
        gender (str): Пол пользователя ('м' для мужчин, 'ж' для женщин).
        weight (float): Вес пользователя в килограммах.
        height (float): Рост пользователя в сантиметрах.
        age (int): Возраст пользователя в годах.
        activity_level (int): Уровень активности (1–5).

    Returns:
        float: Рассчитанная суточная норма калорий в килокалориях.

    Notes:
        Используется базовый метаболический уровень (BMR) с множителями активности:
        1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9.
    """
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