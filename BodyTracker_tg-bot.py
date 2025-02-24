from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from bmi_calculator import handle_weight, handle_height
from water_reminder import (
    show_reminders_menu, toggle_reminders, add_reminder, handle_reminder_time,
    delete_reminder, handle_delete_reminder
)

# Токен вашего бота
BOT_TOKEN = '7748084790:AAEa0bomHqTJCpLD9cR1ez9K6vtsPxhsNoQ'

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Рассчитать индекс массы тела", callback_data='rach')],
        [InlineKeyboardButton("Статистика похудения", callback_data='stat')],
        [InlineKeyboardButton("Рассчитать калории на день", callback_data='kkal')],
        [InlineKeyboardButton("Контроль питания", callback_data='control')],
        [InlineKeyboardButton("Напоминания попить воды", callback_data='reminders')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Как я могу помочь?\nВыберите один из вариантов:",
        reply_markup=reply_markup
    )

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'rach':
        await query.edit_message_text(text="Вы выбрали: Рассчитать индекс массы тела")
        await query.message.reply_text("Введите ваш вес в килограммах (например, 70):")
        context.user_data['state'] = 'waiting_for_weight'
    elif query.data == 'stat':
        await query.edit_message_text(text="Вы выбрали: Посмотреть статистику похудения")
    elif query.data == 'kkal':
        await query.edit_message_text(text="Вы выбрали: Рассчитать калории на день")
    elif query.data == 'control':
        await query.edit_message_text(text="Вы выбрали: Контроль питания")
    elif query.data == 'reminders':
        await show_reminders_menu(update, context)
    elif query.data == 'toggle_reminders':
        await toggle_reminders(update, context)
    elif query.data == 'add_reminder':
        await add_reminder(update, context)
    elif query.data == 'delete_reminder':
        await delete_reminder(update, context)
    elif query.data.startswith('delete_'):
        await handle_delete_reminder(update, context)

# Обработка сообщений от пользователя
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state', None)
    if state == 'waiting_for_weight':
        await handle_weight(update, context)
    elif state == 'waiting_for_height':
        await handle_height(update, context)
    elif state == 'waiting_for_reminder_time':
        await handle_reminder_time(update, context)

# Основная функция
if __name__ == '__main__':
    print("Запуск бота...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Бот работает...")
    app.run_polling()