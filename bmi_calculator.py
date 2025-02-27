from telegram import Update
from telegram.ext import ContextTypes

# Функция для обработки ввода веса
async def handle_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# Функция для обработки ввода роста и расчета ИМТ
async def handle_height(update: Update, context: ContextTypes.DEFAULT_TYPE, start_function):
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