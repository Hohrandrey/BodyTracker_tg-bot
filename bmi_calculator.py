from telegram import Update
from telegram.ext import ContextTypes

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

# Функция для обработки ввода роста и расчета ИМТ
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
        context.user_data['state'] = None  # Сбрасываем состояние
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для роста.")
        context.user_data['state'] = None  # Сбрасываем состояние