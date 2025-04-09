#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إعداد نظام التسجيل
"""

import logging
import sys
import os

def setup_logger(level=logging.INFO):
    """
    إعداد نظام التسجيل
    
    Parameters:
        level: مستوى التسجيل
    
    Returns:
        logging.Logger: مثيل المسجل
    """
    # إنشاء مجلد السجلات إذا لم يكن موجوداً
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # إعداد المسجل الرئيسي
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # التأكد من عدم وجود معالجات مسجلة سابقاً
    if logger.handlers:
        logger.handlers.clear()
    
    # تنسيق السجل
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # معالج وحدة التحكم
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # معالج الملف
    file_handler = logging.FileHandler(os.path.join(log_dir, 'trading_bot.log'), encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
