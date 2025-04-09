from telebot import TeleBot
from telebot.types import Message, CallbackQuery

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def handle_start(message: Message):
        bot.send_message(message.chat.id, "مرحبًا بك في بوت التداول! استخدم الأزرار للبدء.")

    @bot.message_handler(func=lambda message: True)
    def handle_message(message: Message):
        bot.send_message(message.chat.id, f"لقد أرسلت: {message.text}")

def handle_back_navigation(bot: TeleBot, call: CallbackQuery, back_to: str):
    if back_to == 'symbols':
        bot.send_message(call.message.chat.id, "🔙 الرجوع إلى قائمة الرموز.")
    elif back_to == 'strategies':
        bot.send_message(call.message.chat.id, "🔙 الرجوع إلى قائمة الاستراتيجيات.")
    else:
        bot.send_message(call.message.chat.id, "↩️ الرجوع إلى القائمة السابقة.")