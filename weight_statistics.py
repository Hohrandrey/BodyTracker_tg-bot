from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import matplotlib.pyplot as plt
import io

# Глобальный словарь для хранения данных о весе пользователей
user_weight_data = {}

async def show_weight_statistics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображает меню статистики похудения с кнопками 'Ввести вес' и 'Назад'.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий информацию о запросе.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция отправляет сообщение с меню в чат.
    """
    keyboard = [
        [InlineKeyboardButton("Ввести вес", callback_data='enter_weight')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text="Вы выбрали: Статистика похудения",
        reply_markup=reply_markup
    )

async def enter_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрашивает у пользователя ввод текущего веса.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий информацию о запросе.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.

    Returns:
        None: Функция отправляет сообщение с запросом веса и устанавливает состояние ожидания ввода.
    """
    await update.callback_query.edit_message_text(text="Введите ваш текущий вес в килограммах (например, 70.5):")
    context.user_data['state'] = 'waiting_for_weight_stat'

async def handle_weight_stat(update: Update, context: ContextTypes.DEFAULT_TYPE, start_function):
    """Обрабатывает введённый пользователем вес, сохраняет его и строит график.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий текст сообщения.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.
        start_function (callable): Функция для возврата в главное меню после обработки.

    Returns:
        None: Функция отправляет пользователю результат обработки и график, либо сообщение об ошибке.

    Raises:
        ValueError: Если введённое значение не является числом, обрабатывается внутри функции.
    """
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

def create_weight_plot(weights):
    """Создаёт график изменения веса и возвращает его в виде буфера.

    Args:
        weights (list): Список значений веса пользователя.

    Returns:
        io.BytesIO: Буфер с изображением графика в формате PNG.
    """
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

async def back_to_main_menu_from_stat(update: Update, context: ContextTypes.DEFAULT_TYPE, start_function):
    """Возвращает пользователя в главное меню.

    Args:
        update (telegram.Update): Объект обновления от Telegram, содержащий информацию о запросе.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Контекст бота, содержащий данные пользователя.
        start_function (callable): Функция для отображения главного меню.

    Returns:
        None: Функция вызывает start_function для возврата в главное меню.
    """
    # Возврат в главное меню
    await start_function(update, context)