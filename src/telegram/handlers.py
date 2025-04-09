
def handle_back_navigation(call, bot, back_to, language, chat_id):
    if back_to == 'symbols':
        # العودة إلى اختيار الزوج
        bot.edit_message_text(
            "اختر الزوج الذي ترغب في تحليله:" if language == 'ar' else "Choose the pair you want to analyze:",
            chat_id,
            call.message.message_id,
            reply_markup=create_symbol_keyboard(language)
        )
    elif back_to == 'timeframes':
        # العودة إلى اختيار الإطار الزمني
        bot.edit_message_text(
            "اختر الإطار الزمني:" if language == 'ar' else "Choose the timeframe:",
            chat_id,
            call.message.message_id,
            reply_markup=create_timeframe_keyboard(language)
        )
