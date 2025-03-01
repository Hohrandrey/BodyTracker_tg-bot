from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import matplotlib.pyplot as plt
import io

# Глобальный словарь для хранения данных о весе пользователей
user_weight_data = {}

# Обработчик кнопки "Статистика похудения"
async def show_weight_statistics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ввести вес", callback_data='enter_weight')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text="Вы выбрали: Статистика похудения",
        reply_markup=reply_markup
    )

# Обработчик кнопки "Ввести вес"
async def enter_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(text="Введите ваш текущий вес в килограммах (например, 70.5):")
    context.user_data['state'] = 'waiting_for_weight_stat'

# Обработчик ввода веса
async def handle_weight_stat(update: Update, context: ContextTypes.DEFAULT_TYPE, start_function):
    try:
        # Пытаемся преобразовать ввод в число (дробное или целое)
        weight = float(update.message.text)

        # Проверяем, что вес положительный
        if weight <= 0:
            await update.message.reply_text("Вес должен быть положительным числом. Попробуйте снова.")
            return

        user_id = update.message.from_user.id

        # Сохраняем вес пользователя
        if user_id not in user_weight_data:
            user_weight_data[user_id] = []
        user_weight_data[user_id].append(weight)

        # Строим график
        plot = create_weight_plot(user_weight_data[user_id])

        # Отправляем график пользователю
        await update.message.reply_photo(photo=plot)
        await update.message.reply_text("Вес успешно сохранен. График построен.")

        # Возвращаемся в главное меню
        await start_function(update, context)

    except ValueError:
        # Если ввод не является числом
        await update.message.reply_text("Пожалуйста, введите корректное число для веса (например, 70 или 70.5).")

# Функция для создания графика
def create_weight_plot(weights):
    plt.figure()
    plt.plot(weights, marker='o')
    plt.title('Статистика похудения')
    plt.xlabel('Количество замеров')
    plt.ylabel('Вес (кг)')

    # Сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf

# Обработчик кнопки "Назад"
async def back_to_main_menu_from_stat(update: Update, context: ContextTypes.DEFAULT_TYPE, start_function):
    # Возврат в главное меню
    await start_function(update, context)