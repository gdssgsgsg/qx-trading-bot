#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
منطق البوت الرئيسي - إصدار Render المحسن
"""

import logging
import telebot
import time
from functools import wraps

from src.utils.config import load_config
from src.qxbroker.qx_client import QXClient
from src.analysis.signal_generator import SignalGenerator
from src.telegram.handlers import register_handlers

# الحصول على مثيل المسجل
logger = logging.getLogger(__name__)

# تحميل الإعدادات
config = load_config()

# تخزين مؤقت للمستخدمين النشطين لتحسين الأداء
active_users_cache = {}

def rate_limit(limit=3, interval=1):
    """
    مزين للحد من معدل الاستدعاء للوظائف
    
    Parameters:
        limit: الحد الأقصى للاستدعاءات
        interval: الفاصل الزمني بالثواني
    """
    def decorator(func):
        func._calls = []
        
        @wraps(func)
        def wrapped(*args, **kwargs):
            now = time.time()
            # إزالة الاستدعاءات القديمة
            func._calls = [t for t in func._calls if now - t < interval]
            
            # التحقق من تجاوز الحد
            if len(func._calls) >= limit:
                logger.warning(f"تجاوز معدل الاستدعاء للوظيفة: {func.__name__}")
                return None
            
            # إضافة الاستدعاء الحالي
            func._calls.append(now)
            return func(*args, **kwargs)
        
        return wrapped
    return decorator

def initialize_bot():
    """
    تهيئة البوت وإعداد المكونات الضرورية
    
    Returns:
        TeleBot: مثيل البوت المهيأ
    """
    try:
        # إنشاء مثيل البوت
        bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
        
        # تهيئة عميل QXBroker
        qx_client = QXClient()
        
        # سنحاول الاتصال ولكن لن نتوقف إذا فشل الاتصال الأولي
        try:
            qx_client.initialize()
            logger.info("تم تهيئة عميل QXBroker بنجاح")
        except Exception as e:
            logger.warning(f"فشل الاتصال الأولي بـ QXBroker: {e}. سيتم المحاولة لاحقاً.")
        
        # إعداد مولد الإشارات
        signal_generator = SignalGenerator(qx_client)
        logger.info("تم إعداد مولد الإشارات بنجاح")
        
        # تسجيل معالجات الرسائل
        register_handlers(bot, signal_generator, active_users_cache)
        logger.info("تم تسجيل معالجات البوت بنجاح")
        
        return bot
        
    except Exception as e:
        logger.error(f"خطأ أثناء تهيئة البوت: {e}")
        raise

@rate_limit(limit=50, interval=10)  # الحد من معدل المعالجة لتجنب استهلاك موارد زائدة
def process_update(bot, update):
    """
    معالجة تحديث من Telegram Webhook
    
    Parameters:
        bot: مثيل البوت
        update: تحديث تليجرام
    """
    try:
        bot.process_new_updates([update])
    except Exception as e:
        logger.error(f"خطأ أثناء معالجة التحديث: {e}")
