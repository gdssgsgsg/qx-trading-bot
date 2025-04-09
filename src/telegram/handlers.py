            elif back_to == 'symbols':
                # العودة إلى اختيار الزوج
                bot.edit_message_text(
                    "اختر الزوج الذي ترغب في تحليله:" if language == 'ar' else "Choose the pair you want to analyze:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=create_symbol_keyboard(language)
                )
            
            elif back_to == 'timeframes':
                # العودة إلى اختيار الإطار الزمني
                selected_symbol = active_users_cache.get(user_id, {}).get('selected_symbol', 'BTCUSDT')
                bot.edit_message_text(
                    f"اختر الإطار الزمني لتحليل {selected_symbol}:" if language == 'ar' else f"Choose the timeframe for {selected_symbol} analysis:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=create_timeframe_keyboard(language)
                )
        except Exception as e:
            logger.error(f"خطأ في معالج زر العودة: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('refresh_signal_'))
    def handle_refresh_signal(call):
        """معالج زر تحديث الإشارة"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            signal_id = call.data.split('_')[2]
            
            # الحصول على لغة المستخدم
            language = active_users_cache.get(user_id, {}).get('language', 'ar')
            
            # تحديث آخر نشاط
            if user_id in active_users_cache:
                active_users_cache[user_id]['last_activity'] = time.time()
            
            # الحصول على الزوج والإطار الزمني من التخزين المؤقت
            selected_symbol = active_users_cache.get(user_id, {}).get('selected_symbol', 'BTCUSDT')
            selected_timeframe = active_users_cache.get(user_id, {}).get('selected_timeframe', '1h')
            
            # إرسال رسالة معالجة
            bot.edit_message_text(
                f"🔄 جاري تحديث التحليل لـ {selected_symbol} ({selected_timeframe})...",
                chat_id,
                call.message.message_id
            )
            
            # إعادة توليد الإشارة
            signal = signal_generator.generate_signal(selected_symbol, selected_timeframe)
            
            if signal:
                # إرسال الإشارة المحدثة
                send_signal_message(bot, chat_id, signal, call.message.message_id)
            else:
                bot.edit_message_text(
                    f"⚠️ لا توجد إشارة قوية لـ {selected_symbol} على الإطار الزمني {selected_timeframe} حاليًا.",
                    chat_id,
                    call.message.message_id
                )
        except Exception as e:
            logger.error(f"خطأ في معالج تحديث الإشارة: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('settings_'))
    def handle_settings_callback(call):
        """معالج أزرار الإعدادات"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            setting_action = call.data.split('_')[1]
            
            # الحصول على لغة المستخدم
            language = active_users_cache.get(user_id, {}).get('language', 'ar')
            
            # تحديث آخر نشاط
            if user_id in active_users_cache:
                active_users_cache[user_id]['last_activity'] = time.time()
            
            if setting_action == 'notifications_on':
                # تفعيل الإشعارات
                active_users_cache.setdefault(user_id, {})['notification'] = True
                bot.answer_callback_query(call.id, "تم تفعيل الإشعارات بنجاح")
                handle_settings(call.message)
            
            elif setting_action == 'notifications_off':
                # تعطيل الإشعارات
                active_users_cache.setdefault(user_id, {})['notification'] = False
                bot.answer_callback_query(call.id, "تم تعطيل الإشعارات بنجاح")
                handle_settings(call.message)
            
            elif setting_action == 'language':
                # تغيير اللغة
                markup = types.InlineKeyboardMarkup(row_width=2)
                arabic_btn = types.InlineKeyboardButton("العربية 🇸🇦", callback_data='lang_ar')
                english_btn = types.InlineKeyboardButton("English 🇬🇧", callback_data='lang_en')
                markup.add(arabic_btn, english_btn)
                
                bot.edit_message_text(
                    "🌐 اختر لغتك المفضلة / Choose your preferred language:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=markup
                )
        except Exception as e:
            logger.error(f"خطأ في معالج إعدادات الإشعارات: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
    def handle_language_callback(call):
        """معالج اختيار اللغة"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            selected_language = call.data.split('_')[1]
            
            # تحديث لغة المستخدم
            active_users_cache.setdefault(user_id, {})['language'] = selected_language
            
            # إرسال رسالة تأكيد
            if selected_language == 'ar':
                confirmation_text = "✅ تم تغيير اللغة إلى العربية بنجاح."
            else:
                confirmation_text = "✅ Language has been changed to English successfully."
            
            bot.edit_message_text(
                confirmation_text,
                chat_id,
                call.message.message_id,
                reply_markup=None
            )
            
            # إرسال لوحة المفاتيح الرئيسية بعد تغيير اللغة
            bot.send_message(
                chat_id,
                "👇 استخدم لوحة المفاتيح أدناه للوصول إلى الميزات:" if selected_language == 'ar' else "👇 Use the keyboard below to access features:",
                reply_markup=create_main_keyboard(selected_language)
            )
        except Exception as e:
            logger.error(f"خطأ في معالج اختيار اللغة: {e}")
    
    # تسجيل معالجات إضافية كما هو مطلوب
    
    logger.info("تم تسجيل معالجات البوت بنجاح")

def process_analysis(bot, signal_generator, chat_id, user_id, symbol, timeframe, message_id, language):
    """
    معالجة التحليل وإرسال النتائج
    
    Parameters:
        bot: مثيل البوت
        signal_generator: مولد الإشارات
        chat_id: معرف المحادثة
        user_id: معرف المستخدم
        symbol: رمز الزوج
        timeframe: الإطار الزمني
        message_id: معرف رسالة المعالجة
        language: رمز اللغة
    """
    try:
        # توليد الإشارة
        signal = signal_generator.generate_signal(symbol, timeframe)
        
        if signal:
            # إرسال الإشارة
            send_signal_message(bot, chat_id, signal, message_id)
        else:
            # لا توجد إشارة قوية
            bot.edit_message_text(
                f"⚠️ لا توجد إشارة قوية لـ {symbol} على الإطار الزمني {timeframe} حاليًا.\n\nيمكنك تجربة زوج آخر أو إطار زمني مختلف.",
                chat_id,
                message_id,
                reply_markup=create_main_keyboard(language)
            )
        
    except Exception as e:
        logger.error(f"خطأ أثناء معالجة التحليل: {e}")
        bot.edit_message_text(
            f"⚠️ حدث خطأ أثناء تحليل {symbol}. يرجى المحاولة مرة أخرى لاحقًا.",
            chat_id,
            message_id,
            reply_markup=create_main_keyboard(language)
        )

def send_signal_message(bot, chat_id, signal, message_id=None):
    """
    إرسال رسالة الإشارة
    
    Parameters:
        bot: مثيل البوت
        chat_id: معرف المحادثة
        signal: قاموس الإشارة
        message_id: معرف الرسالة للتعديل (اختياري)
    """
    try:
        # تنسيق رسالة الإشارة
        signal_message = f"""
📌 الأصل: {signal['الزوج']} – الإطار الزمني: {signal['الإطار_الزمني']}
🔁 الاتجاه: {signal['الاتجاه']}
{'🟢 الإشارة: شراء ✅' if signal['نوع'] == 'شراء' else '🔴 الإشارة: بيع ✅'}
🎯 نقطة الدخول المقترحة: {signal['نقطة_الدخول']}
🛡️ وقف الخسارة: {signal['وقف_الخسارة']}
📈 الهدف الأول: {signal['الهدف']}
📈 الهدف الثاني: {signal.get('الهدف_الثاني', '-')}
📊 درجة الثقة: {signal['نسبة_الثقة']}%
📍 المؤشرات المستخدمة: {signal['المؤشرات']}

📋 التحليل:
{signal['التحليل'][:500]}... 

⏰ وقت الإشارة: {signal['الوقت']}
"""
        
        # إنشاء أزرار للمتابعة
        markup = types.InlineKeyboardMarkup(row_width=2)
        refresh_btn = types.InlineKeyboardButton("🔄 تحديث التحليل", callback_data=f"refresh_signal_{signal['id']}")
        notify_btn = types.InlineKeyboardButton("🔔 تنبيه عند الوصول للهدف", callback_data=f"notify_signal_{signal['id']}")
        back_btn = types.InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")
        markup.add(refresh_btn, notify_btn)
        markup.add(back_btn)
        
        # إرسال أو تعديل الرسالة
        if message_id:
            bot.edit_message_text(
                signal_message,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            bot.send_message(
                chat_id,
                signal_message,
                parse_mode='Markdown',
                reply_markup=markup
            )
    except Exception as e:
        logger.error(f"خطأ أثناء إرسال رسالة الإشارة: {e}")
        # محاولة إرسال رسالة بسيطة في حالة الفشل
        simple_message = f"إشارة {signal['نوع']} لـ {signal['الزوج']} بثقة {signal['نسبة_الثقة']}%"
        if message_id:
            bot.edit_message_text(simple_message, chat_id, message_id)
        else:
            bot.send_message(chat_id, simple_message)            elif back_to == 'symbols':
                # العودة إلى اختيار الزوج
                bot.edit_message_text(
                    "اختر الزوج الذي ترغب في تحليله:" if language == 'ar' else "Choose the pair you want to analyze:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=create_symbol_keyboard(language)
                )
            
            elif back_to == 'timeframes':
                # العودة إلى اختيار الإطار الزمني
                selected_symbol = active_users_cache.get(user_id, {}).get('selected_symbol', 'BTCUSDT')
                bot.edit_message_text(
                    f"اختر الإطار الزمني لتحليل {selected_symbol}:" if language == 'ar' else f"Choose the timeframe for {selected_symbol} analysis:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=create_timeframe_keyboard(language)
                )
        except Exception as e:
            logger.error(f"خطأ في معالج زر العودة: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('refresh_signal_'))
    def handle_refresh_signal(call):
        """معالج زر تحديث الإشارة"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            signal_id = call.data.split('_')[2]
            
            # الحصول على لغة المستخدم
            language = active_users_cache.get(user_id, {}).get('language', 'ar')
            
            # تحديث آخر نشاط
            if user_id in active_users_cache:
                active_users_cache[user_id]['last_activity'] = time.time()
            
            # الحصول على الزوج والإطار الزمني من التخزين المؤقت
            selected_symbol = active_users_cache.get(user_id, {}).get('selected_symbol', 'BTCUSDT')
            selected_timeframe = active_users_cache.get(user_id, {}).get('selected_timeframe', '1h')
            
            # إرسال رسالة معالجة
            bot.edit_message_text(
                f"🔄 جاري تحديث التحليل لـ {selected_symbol} ({selected_timeframe})...",
                chat_id,
                call.message.message_id
            )
            
            # إعادة توليد الإشارة
            signal = signal_generator.generate_signal(selected_symbol, selected_timeframe)
            
            if signal:
                # إرسال الإشارة المحدثة
                send_signal_message(bot, chat_id, signal, call.message.message_id)
            else:
                bot.edit_message_text(
                    f"⚠️ لا توجد إشارة قوية لـ {selected_symbol} على الإطار الزمني {selected_timeframe} حاليًا.",
                    chat_id,
                    call.message.message_id
                )
        except Exception as e:
            logger.error(f"خطأ في معالج تحديث الإشارة: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('settings_'))
    def handle_settings_callback(call):
        """معالج أزرار الإعدادات"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            setting_action = call.data.split('_')[1]
            
            # الحصول على لغة المستخدم
            language = active_users_cache.get(user_id, {}).get('language', 'ar')
            
            # تحديث آخر نشاط
            if user_id in active_users_cache:
                active_users_cache[user_id]['last_activity'] = time.time()
            
            if setting_action == 'notifications_on':
                # تفعيل الإشعارات
                active_users_cache.setdefault(user_id, {})['notification'] = True
                bot.answer_callback_query(call.id, "تم تفعيل الإشعارات بنجاح")
                handle_settings(call.message)
            
            elif setting_action == 'notifications_off':
                # تعطيل الإشعارات
                active_users_cache.setdefault(user_id, {})['notification'] = False
                bot.answer_callback_query(call.id, "تم تعطيل الإشعارات بنجاح")
                handle_settings(call.message)
            
            elif setting_action == 'language':
                # تغيير اللغة
                markup = types.InlineKeyboardMarkup(row_width=2)
                arabic_btn = types.InlineKeyboardButton("العربية 🇸🇦", callback_data='lang_ar')
                english_btn = types.InlineKeyboardButton("English 🇬🇧", callback_data='lang_en')
                markup.add(arabic_btn, english_btn)
                
                bot.edit_message_text(
                    "🌐 اختر لغتك المفضلة / Choose your preferred language:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=markup
                )
        except Exception as e:
            logger.error(f"خطأ في معالج إعدادات الإشعارات: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
    def handle_language_callback(call):
        """معالج اختيار اللغة"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            selected_language = call.data.split('_')[1]
            
            # تحديث لغة المستخدم
            active_users_cache.setdefault(user_id, {})['language'] = selected_language
            
            # إرسال رسالة تأكيد
            if selected_language == 'ar':
                confirmation_text = "✅ تم تغيير اللغة إلى العربية بنجاح."
            else:
                confirmation_text = "✅ Language has been changed to English successfully."
            
            bot.edit_message_text(
                confirmation_text,
                chat_id,
                call.message.message_id,
                reply_markup=None
            )
            
            # إرسال لوحة المفاتيح الرئيسية بعد تغيير اللغة
            bot.send_message(
                chat_id,
                "👇 استخدم لوحة المفاتيح أدناه للوصول إلى الميزات:" if selected_language == 'ar' else "👇 Use the keyboard below to access features:",
                reply_markup=create_main_keyboard(selected_language)
            )
        except Exception as e:
            logger.error(f"خطأ في معالج اختيار اللغة: {e}")
    
    # تسجيل معالجات إضافية كما هو مطلوب
    
    logger.info("تم تسجيل معالجات البوت بنجاح")

def process_analysis(bot, signal_generator, chat_id, user_id, symbol, timeframe, message_id, language):
    """
    معالجة التحليل وإرسال النتائج
    
    Parameters:
        bot: مثيل البوت
        signal_generator: مولد الإشارات
        chat_id: معرف المحادثة
        user_id: معرف المستخدم
        symbol: رمز الزوج
        timeframe: الإطار الزمني
        message_id: معرف رسالة المعالجة
        language: رمز اللغة
    """
    try:
        # توليد الإشارة
        signal = signal_generator.generate_signal(symbol, timeframe)
        
        if signal:
            # إرسال الإشارة
            send_signal_message(bot, chat_id, signal, message_id)
        else:
            # لا توجد إشارة قوية
            bot.edit_message_text(
                f"⚠️ لا توجد إشارة قوية لـ {symbol} على الإطار الزمني {timeframe} حاليًا.\n\nيمكنك تجربة زوج آخر أو إطار زمني مختلف.",
                chat_id,
                message_id,
                reply_markup=create_main_keyboard(language)
            )
        
    except Exception as e:
        logger.error(f"خطأ أثناء معالجة التحليل: {e}")
        bot.edit_message_text(
            f"⚠️ حدث خطأ أثناء تحليل {symbol}. يرجى المحاولة مرة أخرى لاحقًا.",
            chat_id,
            message_id,
            reply_markup=create_main_keyboard(language)
        )

def send_signal_message(bot, chat_id, signal, message_id=None):
    """
    إرسال رسالة الإشارة
    
    Parameters:
        bot: مثيل البوت
        chat_id: معرف المحادثة
        signal: قاموس الإشارة
        message_id: معرف الرسالة للتعديل (اختياري)
    """
    try:
        # تنسيق رسالة الإشارة
        signal_message = f"""
📌 الأصل: {signal['الزوج']} – الإطار الزمني: {signal['الإطار_الزمني']}
🔁 الاتجاه: {signal['الاتجاه']}
{'🟢 الإشارة: شراء ✅' if signal['نوع'] == 'شراء' else '🔴 الإشارة: بيع ✅'}
🎯 نقطة الدخول المقترحة: {signal['نقطة_الدخول']}
🛡️ وقف الخسارة: {signal['وقف_الخسارة']}
📈 الهدف الأول: {signal['الهدف']}
📈 الهدف الثاني: {signal.get('الهدف_الثاني', '-')}
📊 درجة الثقة: {signal['نسبة_الثقة']}%
📍 المؤشرات المستخدمة: {signal['المؤشرات']}

📋 التحليل:
{signal['التحليل'][:500]}... 

⏰ وقت الإشارة: {signal['الوقت']}
"""
        
        # إنشاء أزرار للمتابعة
        markup = types.InlineKeyboardMarkup(row_width=2)
        refresh_btn = types.InlineKeyboardButton("🔄 تحديث التحليل", callback_data=f"refresh_signal_{signal['id']}")
        notify_btn = types.InlineKeyboardButton("🔔 تنبيه عند الوصول للهدف", callback_data=f"notify_signal_{signal['id']}")
        back_btn = types.InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")
        markup.add(refresh_btn, notify_btn)
        markup.add(back_btn)
        
        # إرسال أو تعديل الرسالة
        if message_id:
            bot.edit_message_text(
                signal_message,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            bot.send_message(
                chat_id,
                signal_message,
                parse_mode='Markdown',
                reply_markup=markup
            )
    except Exception as e:
        logger.error(f"خطأ أثناء إرسال رسالة الإشارة: {e}")
        # محاولة إرسال رسالة بسيطة في حالة الفشل
        simple_message = f"إشارة {signal['نوع']} لـ {signal['الزوج']} بثقة {signal['نسبة_الثقة']}%"
        if message_id:
            bot.edit_message_text(simple_message, chat_id, message_id)
        else:
            bot.send_message(chat_id, simple_message)            elif back_to == 'symbols':
                # العودة إلى اختيار الزوج
                bot.edit_message_text(
                    "اختر الزوج الذي ترغب في تحليله:" if language == 'ar' else "Choose the pair you want to analyze:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=create_symbol_keyboard(language)
                )
            
            elif back_to == 'timeframes':
                # العودة إلى اختيار الإطار الزمني
                selected_symbol = active_users_cache.get(user_id, {}).get('selected_symbol', 'BTCUSDT')
                bot.edit_message_text(
                    f"اختر الإطار الزمني لتحليل {selected_symbol}:" if language == 'ar' else f"Choose the timeframe for {selected_symbol} analysis:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=create_timeframe_keyboard(language)
                )
        except Exception as e:
            logger.error(f"خطأ في معالج زر العودة: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('refresh_signal_'))
    def handle_refresh_signal(call):
        """معالج زر تحديث الإشارة"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            signal_id = call.data.split('_')[2]
            
            # الحصول على لغة المستخدم
            language = active_users_cache.get(user_id, {}).get('language', 'ar')
            
            # تحديث آخر نشاط
            if user_id in active_users_cache:
                active_users_cache[user_id]['last_activity'] = time.time()
            
            # الحصول على الزوج والإطار الزمني من التخزين المؤقت
            selected_symbol = active_users_cache.get(user_id, {}).get('selected_symbol', 'BTCUSDT')
            selected_timeframe = active_users_cache.get(user_id, {}).get('selected_timeframe', '1h')
            
            # إرسال رسالة معالجة
            bot.edit_message_text(
                f"🔄 جاري تحديث التحليل لـ {selected_symbol} ({selected_timeframe})...",
                chat_id,
                call.message.message_id
            )
            
            # إعادة توليد الإشارة
            signal = signal_generator.generate_signal(selected_symbol, selected_timeframe)
            
            if signal:
                # إرسال الإشارة المحدثة
                send_signal_message(bot, chat_id, signal, call.message.message_id)
            else:
                bot.edit_message_text(
                    f"⚠️ لا توجد إشارة قوية لـ {selected_symbol} على الإطار الزمني {selected_timeframe} حاليًا.",
                    chat_id,
                    call.message.message_id
                )
        except Exception as e:
            logger.error(f"خطأ في معالج تحديث الإشارة: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('settings_'))
    def handle_settings_callback(call):
        """معالج أزرار الإعدادات"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            setting_action = call.data.split('_')[1]
            
            # الحصول على لغة المستخدم
            language = active_users_cache.get(user_id, {}).get('language', 'ar')
            
            # تحديث آخر نشاط
            if user_id in active_users_cache:
                active_users_cache[user_id]['last_activity'] = time.time()
            
            if setting_action == 'notifications_on':
                # تفعيل الإشعارات
                active_users_cache.setdefault(user_id, {})['notification'] = True
                bot.answer_callback_query(call.id, "تم تفعيل الإشعارات بنجاح")
                handle_settings(call.message)
            
            elif setting_action == 'notifications_off':
                # تعطيل الإشعارات
                active_users_cache.setdefault(user_id, {})['notification'] = False
                bot.answer_callback_query(call.id, "تم تعطيل الإشعارات بنجاح")
                handle_settings(call.message)
            
            elif setting_action == 'language':
                # تغيير اللغة
                markup = types.InlineKeyboardMarkup(row_width=2)
                arabic_btn = types.InlineKeyboardButton("العربية 🇸🇦", callback_data='lang_ar')
                english_btn = types.InlineKeyboardButton("English 🇬🇧", callback_data='lang_en')
                markup.add(arabic_btn, english_btn)
                
                bot.edit_message_text(
                    "🌐 اختر لغتك المفضلة / Choose your preferred language:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=markup
                )
        except Exception as e:
            logger.error(f"خطأ في معالج إعدادات الإشعارات: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
    def handle_language_callback(call):
        """معالج اختيار اللغة"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            selected_language = call.data.split('_')[1]
            
            # تحديث لغة المستخدم
            active_users_cache.setdefault(user_id, {})['language'] = selected_language
            
            # إرسال رسالة تأكيد
            if selected_language == 'ar':
                confirmation_text = "✅ تم تغيير اللغة إلى العربية بنجاح."
            else:
                confirmation_text = "✅ Language has been changed to English successfully."
            
            bot.edit_message_text(
                confirmation_text,
                chat_id,
                call.message.message_id,
                reply_markup=None
            )
            
            # إرسال لوحة المفاتيح الرئيسية بعد تغيير اللغة
            bot.send_message(
                chat_id,
                "👇 استخدم لوحة المفاتيح أدناه للوصول إلى الميزات:" if selected_language == 'ar' else "👇 Use the keyboard below to access features:",
                reply_markup=create_main_keyboard(selected_language)
            )
        except Exception as e:
            logger.error(f"خطأ في معالج اختيار اللغة: {e}")
    
    # تسجيل معالجات إضافية كما هو مطلوب
    
    logger.info("تم تسجيل معالجات البوت بنجاح")

def process_analysis(bot, signal_generator, chat_id, user_id, symbol, timeframe, message_id, language):
    """
    معالجة التحليل وإرسال النتائج
    
    Parameters:
        bot: مثيل البوت
        signal_generator: مولد الإشارات
        chat_id: معرف المحادثة
        user_id: معرف المستخدم
        symbol: رمز الزوج
        timeframe: الإطار الزمني
        message_id: معرف رسالة المعالجة
        language: رمز اللغة
    """
    try:
        # توليد الإشارة
        signal = signal_generator.generate_signal(symbol, timeframe)
        
        if signal:
            # إرسال الإشارة
            send_signal_message(bot, chat_id, signal, message_id)
        else:
            # لا توجد إشارة قوية
            bot.edit_message_text(
                f"⚠️ لا توجد إشارة قوية لـ {symbol} على الإطار الزمني {timeframe} حاليًا.\n\nيمكنك تجربة زوج آخر أو إطار زمني مختلف.",
                chat_id,
                message_id,
                reply_markup=create_main_keyboard(language)
            )
        
    except Exception as e:
        logger.error(f"خطأ أثناء معالجة التحليل: {e}")
        bot.edit_message_text(
            f"⚠️ حدث خطأ أثناء تحليل {symbol}. يرجى المحاولة مرة أخرى لاحقًا.",
            chat_id,
            message_id,
            reply_markup=create_main_keyboard(language)
        )

def send_signal_message(bot, chat_id, signal, message_id=None):
    """
    إرسال رسالة الإشارة
    
    Parameters:
        bot: مثيل البوت
        chat_id: معرف المحادثة
        signal: قاموس الإشارة
        message_id: معرف الرسالة للتعديل (اختياري)
    """
    try:
        # تنسيق رسالة الإشارة
        signal_message = f"""
📌 الأصل: {signal['الزوج']} – الإطار الزمني: {signal['الإطار_الزمني']}
🔁 الاتجاه: {signal['الاتجاه']}
{'🟢 الإشارة: شراء ✅' if signal['نوع'] == 'شراء' else '🔴 الإشارة: بيع ✅'}
🎯 نقطة الدخول المقترحة: {signal['نقطة_الدخول']}
🛡️ وقف الخسارة: {signal['وقف_الخسارة']}
📈 الهدف الأول: {signal['الهدف']}
📈 الهدف الثاني: {signal.get('الهدف_الثاني', '-')}
📊 درجة الثقة: {signal['نسبة_الثقة']}%
📍 المؤشرات المستخدمة: {signal['المؤشرات']}

📋 التحليل:
{signal['التحليل'][:500]}... 

⏰ وقت الإشارة: {signal['الوقت']}
"""
        
        # إنشاء أزرار للمتابعة
        markup = types.InlineKeyboardMarkup(row_width=2)
        refresh_btn = types.InlineKeyboardButton("🔄 تحديث التحليل", callback_data=f"refresh_signal_{signal['id']}")
        notify_btn = types.InlineKeyboardButton("🔔 تنبيه عند الوصول للهدف", callback_data=f"notify_signal_{signal['id']}")
        back_btn = types.InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")
        markup.add(refresh_btn, notify_btn)
        markup.add(back_btn)
        
        # إرسال أو تعديل الرسالة
        if message_id:
            bot.edit_message_text(
                signal_message,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            bot.send_message(
                chat_id,
                signal_message,
                parse_mode='Markdown',
                reply_markup=markup
            )
    except Exception as e:
        logger.error(f"خطأ أثناء إرسال رسالة الإشارة: {e}")
        # محاولة إرسال رسالة بسيطة في حالة الفشل
        simple_message = f"إشارة {signal['نوع']} لـ {signal['الزوج']} بثقة {signal['نسبة_الثقة']}%"
        if message_id:
            bot.edit_message_text(simple_message, chat_id, message_id)
        else:
            bot.send_message(chat_id, simple_message)
            elif back_to == 'symbols':
                # العودة إلى اختيار الزوج
                bot.edit_message_text(
                    "اختر الزوج الذي ترغب في تحليله:" if language == 'ar' else "Choose the pair you want to analyze:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=create_symbol_keyboard(language)
                )
            
            elif back_to == 'timeframes':
                # العودة إلى اختيار الإطار الزمني
                selected_symbol = active_users_cache.get(user_id, {}).get('selected_symbol', 'BTCUSDT')
                bot.edit_message_text(
                    f"اختر الإطار الزمني لتحليل {selected_symbol}:" if language == 'ar' else f"Choose the timeframe for {selected_symbol} analysis:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=create_timeframe_keyboard(language)
                )
        except Exception as e:
            logger.error(f"خطأ في معالج زر العودة: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('refresh_signal_'))
    def handle_refresh_signal(call):
        """معالج زر تحديث الإشارة"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            signal_id = call.data.split('_')[2]
            
            # الحصول على لغة المستخدم
            language = active_users_cache.get(user_id, {}).get('language', 'ar')
            
            # تحديث آخر نشاط
            if user_id in active_users_cache:
                active_users_cache[user_id]['last_activity'] = time.time()
            
            # الحصول على الزوج والإطار الزمني من التخزين المؤقت
            selected_symbol = active_users_cache.get(user_id, {}).get('selected_symbol', 'BTCUSDT')
            selected_timeframe = active_users_cache.get(user_id, {}).get('selected_timeframe', '1h')
            
            # إرسال رسالة معالجة
            bot.edit_message_text(
                f"🔄 جاري تحديث التحليل لـ {selected_symbol} ({selected_timeframe})...",
                chat_id,
                call.message.message_id
            )
            
            # إعادة توليد الإشارة
            signal = signal_generator.generate_signal(selected_symbol, selected_timeframe)
            
            if signal:
                # إرسال الإشارة المحدثة
                send_signal_message(bot, chat_id, signal, call.message.message_id)
            else:
                bot.edit_message_text(
                    f"⚠️ لا توجد إشارة قوية لـ {selected_symbol} على الإطار الزمني {selected_timeframe} حاليًا.",
                    chat_id,
                    call.message.message_id
                )
        except Exception as e:
            logger.error(f"خطأ في معالج تحديث الإشارة: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('settings_'))
    def handle_settings_callback(call):
        """معالج أزرار الإعدادات"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            setting_action = call.data.split('_')[1]
            
            # الحصول على لغة المستخدم
            language = active_users_cache.get(user_id, {}).get('language', 'ar')
            
            # تحديث آخر نشاط
            if user_id in active_users_cache:
                active_users_cache[user_id]['last_activity'] = time.time()
            
            if setting_action == 'notifications_on':
                # تفعيل الإشعارات
                active_users_cache.setdefault(user_id, {})['notification'] = True
                bot.answer_callback_query(call.id, "تم تفعيل الإشعارات بنجاح")
                handle_settings(call.message)
            
            elif setting_action == 'notifications_off':
                # تعطيل الإشعارات
                active_users_cache.setdefault(user_id, {})['notification'] = False
                bot.answer_callback_query(call.id, "تم تعطيل الإشعارات بنجاح")
                handle_settings(call.message)
            
            elif setting_action == 'language':
                # تغيير اللغة
                markup = types.InlineKeyboardMarkup(row_width=2)
                arabic_btn = types.InlineKeyboardButton("العربية 🇸🇦", callback_data='lang_ar')
                english_btn = types.InlineKeyboardButton("English 🇬🇧", callback_data='lang_en')
                markup.add(arabic_btn, english_btn)
                
                bot.edit_message_text(
                    "🌐 اختر لغتك المفضلة / Choose your preferred language:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=markup
                )
        except Exception as e:
            logger.error(f"خطأ في معالج إعدادات الإشعارات: {e}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
    def handle_language_callback(call):
        """معالج اختيار اللغة"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            selected_language = call.data.split('_')[1]
            
            # تحديث لغة المستخدم
            active_users_cache.setdefault(user_id, {})['language'] = selected_language
            
            # إرسال رسالة تأكيد
            if selected_language == 'ar':
                confirmation_text = "✅ تم تغيير اللغة إلى العربية بنجاح."
            else:
                confirmation_text = "✅ Language has been changed to English successfully."
            
            bot.edit_message_text(
                confirmation_text,
                chat_id,
                call.message.message_id,
                reply_markup=None
            )
            
            # إرسال لوحة المفاتيح الرئيسية بعد تغيير اللغة
            bot.send_message(
                chat_id,
                "👇 استخدم لوحة المفاتيح أدناه للوصول إلى الميزات:" if selected_language == 'ar' else "👇 Use the keyboard below to access features:",
                reply_markup=create_main_keyboard(selected_language)
            )
        except Exception as e:
            logger.error(f"خطأ في معالج اختيار اللغة: {e}")
    
    # تسجيل معالجات إضافية كما هو مطلوب
    
    logger.info("تم تسجيل معالجات البوت بنجاح")

def process_analysis(bot, signal_generator, chat_id, user_id, symbol, timeframe, message_id, language):
    """
    معالجة التحليل وإرسال النتائج
    
    Parameters:
        bot: مثيل البوت
        signal_generator: مولد الإشارات
        chat_id: معرف المحادثة
        user_id: معرف المستخدم
        symbol: رمز الزوج
        timeframe: الإطار الزمني
        message_id: معرف رسالة المعالجة
        language: رمز اللغة
    """
    try:
        # توليد الإشارة
        signal = signal_generator.generate_signal(symbol, timeframe)
        
        if signal:
            # إرسال الإشارة
            send_signal_message(bot, chat_id, signal, message_id)
        else:
            # لا توجد إشارة قوية
            bot.edit_message_text(
                f"⚠️ لا توجد إشارة قوية لـ {symbol} على الإطار الزمني {timeframe} حاليًا.\n\nيمكنك تجربة زوج آخر أو إطار زمني مختلف.",
                chat_id,
                message_id,
                reply_markup=create_main_keyboard(language)
            )
        
    except Exception as e:
        logger.error(f"خطأ أثناء معالجة التحليل: {e}")
        bot.edit_message_text(
            f"⚠️ حدث خطأ أثناء تحليل {symbol}. يرجى المحاولة مرة أخرى لاحقًا.",
            chat_id,
            message_id,
            reply_markup=create_main_keyboard(language)
        )

def send_signal_message(bot, chat_id, signal, message_id=None):
    """
    إرسال رسالة الإشارة
    
    Parameters:
        bot: مثيل البوت
        chat_id: معرف المحادثة
        signal: قاموس الإشارة
        message_id: معرف الرسالة للتعديل (اختياري)
    """
    try:
        # تنسيق رسالة الإشارة
        signal_message = f"""
📌 الأصل: {signal['الزوج']} – الإطار الزمني: {signal['الإطار_الزمني']}
🔁 الاتجاه: {signal['الاتجاه']}
{'🟢 الإشارة: شراء ✅' if signal['نوع'] == 'شراء' else '🔴 الإشارة: بيع ✅'}
🎯 نقطة الدخول المقترحة: {signal['نقطة_الدخول']}
🛡️ وقف الخسارة: {signal['وقف_الخسارة']}
📈 الهدف الأول: {signal['الهدف']}
📈 الهدف الثاني: {signal.get('الهدف_الثاني', '-')}
📊 درجة الثقة: {signal['نسبة_الثقة']}%
📍 المؤشرات المستخدمة: {signal['المؤشرات']}

📋 التحليل:
{signal['التحليل'][:500]}... 

⏰ وقت الإشارة: {signal['الوقت']}
"""
        
        # إنشاء أزرار للمتابعة
        markup = types.InlineKeyboardMarkup(row_width=2)
        refresh_btn = types.InlineKeyboardButton("🔄 تحديث التحليل", callback_data=f"refresh_signal_{signal['id']}")
        notify_btn = types.InlineKeyboardButton("🔔 تنبيه عند الوصول للهدف", callback_data=f"notify_signal_{signal['id']}")
        back_btn = types.InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")
        markup.add(refresh_btn, notify_btn)
        markup.add(back_btn)
        
        # إرسال أو تعديل الرسالة
        if message_id:
            bot.edit_message_text(
                signal_message,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            bot.send_message(
                chat_id,
                signal_message,
                parse_mode='Markdown',
                reply_markup=markup
            )
    except Exception as e:
        logger.error(f"خطأ أثناء إرسال رسالة الإشارة: {e}")
        # محاولة إرسال رسالة بسيطة في حالة الفشل
        simple_message = f"إشارة {signal['نوع']} لـ {signal['الزوج']} بثقة {signal['نسبة_الثقة']}%"
        if message_id:
            bot.edit_message_text(simple_message, chat_id, message_id)
        else:
            bot.send_message(chat_id, simple_message)


