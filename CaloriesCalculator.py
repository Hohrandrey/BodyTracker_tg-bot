# CaloriesCalculator.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_calories_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        text="Вы выбрали: Рассчитать калории на день\n(функция в разработке)"
    )
