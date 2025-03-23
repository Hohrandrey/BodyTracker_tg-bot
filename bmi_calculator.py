from telegram import Update
from telegram.ext import ContextTypes

async def handle_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает введённый пользователем вес и запрашивает рост.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий текст сообщения.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция сохраняет вес, запрашивает рост или отправляет сообщение об ошибке.

    Raises:
        ValueError: Если введённое значение не является числом (обрабатывается внутри функции).
    """
    try:
        # Пытаемся преобразовать ввод в число (дробное или целое)
        weight = float(update.message.text)

        # Проверяем, что вес положительный
        if weight <= 0:
            await update.message.reply_text("Вес должен быть положительным числом. Попробуйте снова.")
            return

        # Сохраняем вес в контексте
        context.user_data['weight'] = weight
        await update.message.reply_text("Введите ваш рост в сантиметрах (например, 175.5):")
        context.user_data['state'] = 'waiting_for_height'  # Устанавливаем состояние ожидания роста

    except ValueError:
        # Если ввод не является числом
        await update.message.reply_text("Пожалуйста, введите корректное число для веса (например, 70 или 70.5).")

async def handle_height(update: Update, context: ContextTypes.DEFAULT_TYPE, start_function):
    """Обрабатывает введённый рост, рассчитывает ИМТ и возвращает пользователя в главное меню.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий текст сообщения.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.
        start_function (callable): Функция для возврата в главное меню после расчёта.

    Returns:
        None: Функция рассчитывает ИМТ, отправляет результат или сообщение об ошибке, затем возвращает в меню.

    Raises:
        ValueError: Если введённое значение не является числом (обрабатывается внутри функции).

    Notes:
        Требует, чтобы вес был сохранён в context.user_data['weight'] до вызова.
    """
    try:
        # Пытаемся преобразовать ввод в число (дробное или целое)
        height = float(update.message.text)

        # Проверяем, что рост положительный
        if height <= 0:
            await update.message.reply_text("Рост должен быть положительным числом. Попробуйте снова.")
            return

        # Сохраняем рост в контексте
        context.user_data['height'] = height

        # Получаем вес и рост из контекста
        weight = context.user_data['weight']
        height_in_meters = height / 100  # Переводим рост в метры

        # Рассчитываем ИМТ
        bmi = weight / (height_in_meters ** 2)
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
        context.user_data['state'] = None  # Сбрасываем состояние

        # Возвращаемся в главное меню
        await start_function(update, context)

    except ValueError:
        # Если ввод не является числом
        await update.message.reply_text("Пожалуйста, введите корректное число для роста (например, 175 или 175.5).")
        context.user_data['state'] = None  # Сбрасываем состояние