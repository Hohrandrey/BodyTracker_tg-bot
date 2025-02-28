from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_calories_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[...]]  # Кнопки выбора пола
    await update.callback_query.edit_message_text(
        text="Вы выбрали: Рассчитать калории на день\n(функция в разработке)"
    )
    context.user_data['state'] = 'waiting_for_calories_gender'

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обработка выбора пола
    await query.edit_message_text("Введите ваш возраст:")
    context.user_data['state'] = 'waiting_for_calories_age'

async def handle_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Базовая валидация возраста
    context.user_data['age'] = age
    await update.message.reply_text("Возраст сохранен!")  # Временный ответ
