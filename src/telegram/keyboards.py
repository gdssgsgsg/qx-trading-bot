#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
لوحات مفاتيح تليجرام
"""

import logging
from telebot import types

logger = logging.getLogger(__name__)

def create_main_keyboard(language="ar"):
    """
    إنشاء لوحة المفاتيح الرئيسية
    
    Parameters:
        language: رمز اللغة (ar للعربية أو en للإنجليزية)
    
    Returns:
        ReplyKeyboardMarkup: لوحة المفاتيح الرئيسية
    """
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    if language == "ar":
        item1 = types.KeyboardButton('📊 تحليل سريع')
        item2 = types.KeyboardButton('📈 أحدث إشارة')
        item3 = types.KeyboardButton('⚙️ الإعدادات')
        item4 = types.KeyboardButton('ℹ️ المساعدة')
    else:
        item1 = types.KeyboardButton('📊 Quick Analysis')
        item2 = types.KeyboardButton('📈 Latest Signal')
        item3 = types.KeyboardButton('⚙️ Settings')
        item4 = types.KeyboardButton('ℹ️ Help')
    
    markup.add(item1, item2)
    markup.add(item3, item4)
    
    return markup

def create_settings_keyboard(language="ar"):
    """
    إنشاء لوحة مفاتيح الإعدادات
    
    Parameters:
        language: رمز اللغة (ar للعربية أو en للإنجليزية)
    
    Returns:
        InlineKeyboardMarkup: لوحة مفاتيح الإعدادات
    """
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    if language == "ar":
        item1 = types.InlineKeyboardButton("🔔 تفعيل الإشعارات", callback_data='settings_notifications_on')
        item2 = types.InlineKeyboardButton("🔕 تعطيل الإشعارات", callback_data='settings_notifications_off')
        item3 = types.InlineKeyboardButton("🌐 تغيير اللغة", callback_data='settings_language')
        item4 = types.InlineKeyboardButton("🔙 العودة", callback_data='back_to_main')
    else:
        item1 = types.InlineKeyboardButton("🔔 Enable Notifications", callback_data='settings_notifications_on')
        item2 = types.InlineKeyboardButton("🔕 Disable Notifications", callback_data='settings_notifications_off')
        item3 = types.InlineKeyboardButton("🌐 Change Language", callback_data='settings_language')
        item4 = types.InlineKeyboardButton("🔙 Back", callback_data='back_to_main')
    
    markup.add(item1, item2)
    markup.add(item3)
    markup.add(item4)
    
    return markup

def create_symbol_keyboard(language="ar"):
    """
    إنشاء لوحة مفاتيح لاختيار الزوج
    
    Parameters:
        language: رمز اللغة (ar للعربية أو en للإنجليزية)
    
    Returns:
        InlineKeyboardMarkup: لوحة مفاتيح الأزواج
    """
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    # العملات المشفرة
    btc = types.InlineKeyboardButton("BTC/USDT", callback_data='symbol_BTCUSDT')
    eth = types.InlineKeyboardButton("ETH/USDT", callback_data='symbol_ETHUSDT')
    bnb = types.InlineKeyboardButton("BNB/USDT", callback_data='symbol_BNBUSDT')
    
    # العملات الأجنبية
    eurusd = types.InlineKeyboardButton("EUR/USD", callback_data='symbol_EURUSD')
    gbpusd = types.InlineKeyboardButton("GBP/USD", callback_data='symbol_GBPUSD')
    usdjpy = types.InlineKeyboardButton("USD/JPY", callback_data='symbol_USDJPY')
    
    # السلع
    gold = types.InlineKeyboardButton("GOLD", callback_data='symbol_XAUUSD')
    
    # العودة
    back = types.InlineKeyboardButton("🔙 العودة" if language == "ar" else "🔙 Back", callback_data='back_to_main')
    
    markup.add(btc, eth, bnb)
    markup.add(eurusd, gbpusd, usdjpy)
    markup.add(gold)
    markup.add(back)
    
    return markup

def create_timeframe_keyboard(language="ar"):
    """
    إنشاء لوحة مفاتيح لاختيار الإطار الزمني
    
    Parameters:
        language: رمز اللغة (ar للعربية أو en للإنجليزية)
    
    Returns:
        InlineKeyboardMarkup: لوحة مفاتيح الأطر الزمنية
    """
    markup = types.InlineKeyboardMarkup(row_width=4)
    
    # الأطر الزمنية
    m5 = types.InlineKeyboardButton("5 د" if language == "ar" else "5m", callback_data='tf_5m')
    m15 = types.InlineKeyboardButton("15 د" if language == "ar" else "15m", callback_data='tf_15m')
    m30 = types.InlineKeyboardButton("30 د" if language == "ar" else "30m", callback_data='tf_30m')
    h1 = types.InlineKeyboardButton("1 س" if language == "ar" else "1h", callback_data='tf_1h')
    h4 = types.InlineKeyboardButton("4 س" if language == "ar" else "4h", callback_data='tf_4h')
    d1 = types.InlineKeyboardButton("يوم" if language == "ar" else "1d", callback_data='tf_1d')
    
    # العودة
    back = types.InlineKeyboardButton("🔙 العودة" if language == "ar" else "🔙 Back", callback_data='back_to_symbols')
    
    markup.add(m5, m15, m30, h1)
    markup.add(h4, d1)
    markup.add(back)
    
    return markup

def create_analysis_options_keyboard(language="ar"):
    """
    إنشاء لوحة مفاتيح لخيارات التحليل
    
    Parameters:
        language: رمز اللغة (ar للعربية أو en للإنجليزية)
    
    Returns:
        InlineKeyboardMarkup: لوحة مفاتيح خيارات التحليل
    """
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    if language == "ar":
        item1 = types.InlineKeyboardButton("📊 تحليل فني فقط", callback_data='analysis_technical')
        item2 = types.InlineKeyboardButton("🔮 تحليل شامل", callback_data='analysis_full')
        item3 = types.InlineKeyboardButton("🔙 العودة", callback_data='back_to_timeframes')
    else:
        item1 = types.InlineKeyboardButton("📊 Technical Only", callback_data='analysis_technical')
        item2 = types.InlineKeyboardButton("🔮 Full Analysis", callback_data='analysis_full')
        item3 = types.InlineKeyboardButton("🔙 Back", callback_data='back_to_timeframes')
    
    markup.add(item1, item2)
    markup.add(item3)
    
    return markup
