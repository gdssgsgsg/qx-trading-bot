#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
نقطة البداية لبوت التداول - إصدار Render المُحسّن
"""

import os
import logging
import threading
import time
from flask import Flask, request, jsonify

from src.utils.config import load_config
from src.utils.logger import setup_logger

# إعداد التسجيل
logger = setup_logger()
logger.info("بدء تشغيل بوت التداول - إصدار Render")

# تحميل الإعدادات
config = load_config()
TOKEN = config.TELEGRAM_BOT_TOKEN

# إنشاء تطبيق Flask
app = Flask(__name__)

# استدعاء تهيئة البوت
# نؤخر الاستيراد لضمان تهيئة logger أولاً
from bot import initialize_bot, process_update
import telebot

# إنشاء البوت وتهيئته
bot = initialize_bot()

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    """معالج webhook لتلقي تحديثات تليجرام"""
    try:
        json_data = request.get_json()
        update = telebot.types.Update.de_json(json_data)
        process_update(bot, update)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"خطأ في معالجة التحديث: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/', methods=['GET'])
def index():
    """صفحة الترحيب البسيطة والتأكد من أن البوت يعمل"""
    return "بوت التداول يعمل! 🚀"

@app.route('/health', methods=['GET'])
def health_check():
    """نقطة نهاية فحص الصحة لمراقبة حالة البوت"""
    return jsonify({"status": "healthy", "version": "1.0.0"})

def set_webhook():
    """إعداد webhook مع تليجرام"""
    try:
        # الحصول على رابط التطبيق من متغيرات البيئة أو استخدام قيمة افتراضية للاختبار المحلي
        app_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://your-app-name.onrender.com')
        webhook_url = f"{app_url}/{TOKEN}"
        
        # حذف أي webhook سابق وإعداد الجديد
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=webhook_url)
        logger.info(f"تم إعداد webhook على: {webhook_url}")
    except Exception as e:
        logger.error(f"خطأ في إعداد webhook: {e}")

def start_polling_fallback():
    """
    آلية احتياطية للاستطلاع في حالة فشل webhook
    تستخدم فقط في بيئة التطوير المحلية
    """
    if not os.environ.get('RENDER_EXTERNAL_URL'):
        logger.info("بدء وضع الاستطلاع الاحتياطي (للتطوير المحلي فقط)")
        bot.remove_webhook()
        bot.polling(none_stop=True, timeout=60)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    
    # إعداد webhook عند بدء التشغيل
    threading.Thread(target=set_webhook).start()
    
    # في بيئة التطوير المحلية، استخدم آلية الاستطلاع الاحتياطية
    if not os.environ.get('RENDER_EXTERNAL_URL'):
        threading.Thread(target=start_polling_fallback).start()
    
    # تشغيل خادم Flask
    app.run(host='0.0.0.0', port=port)
