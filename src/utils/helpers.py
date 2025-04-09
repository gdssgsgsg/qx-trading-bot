#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
وظائف مساعدة متنوعة
"""

import logging
import time
from functools import lru_cache, wraps

logger = logging.getLogger(__name__)

def singleton(cls):
    """
    مزين (decorator) للنمط الفردي (Singleton)
    يضمن أن الفئة لديها مثيل واحد فقط
    
    Parameters:
        cls: الفئة المراد تطبيق النمط عليها
    
    Returns:
        callable: دالة للحصول على مثيل الفئة
    """
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

def rate_limit(calls=5, period=1):
    """
    مزين للحد من معدل استدعاء الدالة
    
    Parameters:
        calls: الحد الأقصى لعدد الاستدعاءات
        period: الفترة الزمنية بالثواني
    
    Returns:
        callable: دالة مزينة بحد معدل الاستدعاء
    """
    def decorator(func):
        # قائمة لتخزين أوقات الاستدعاءات
        func.last_calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # إزالة الاستدعاءات القديمة
            func.last_calls = [t for t in func.last_calls if now - t < period]
            
            # التحقق من عدد الاستدعاءات المتبقية
            if len(func.last_calls) >= calls:
                # تم تجاوز الحد
                logger.warning(f"تم تجاوز معدل الاستدعاء للدالة {func.__name__}")
                return None
            
            # إضافة الاستدعاء الحالي وتنفيذ الدالة
            func.last_calls.append(now)
            return func(*args, **kwargs)
            
        return wrapper
    return decorator

@lru_cache(maxsize=100)
def format_price(price, symbol=None):
    """
    تنسيق السعر بالدقة المناسبة
    
    Parameters:
        price: السعر المراد تنسيقه
        symbol: رمز الزوج (اختياري)
    
    Returns:
        float: السعر بعد التنسيق
    """
    try:
        # تحديد الدقة بناءً على الزوج
        precision = 2  # القيمة الافتراضية
        
        if symbol:
            if "BTC" in symbol:
                precision = 1
            elif "ETH" in symbol or "BNB" in symbol:
                precision = 2
            elif "USDT" in symbol:
                precision = 2
            elif "USD" in symbol:
                precision = 4
            elif "EUR" in symbol or "GBP" in symbol:
                precision = 5
            elif "XAU" in symbol:  # الذهب
                precision = 2
            
        # ضبط الدقة بناءً على قيمة السعر
        if price < 0.1:
            precision = max(precision, 6)
        elif price < 1:
            precision = max(precision, 5)
        elif price < 10:
            precision = max(precision, 4)
        elif price < 100:
            precision = max(precision, 3)
        elif price < 1000:
            precision = max(precision, 2)
        
        return round(float(price), precision)
        
    except Exception as e:
        logger.error(f"خطأ في تنسيق السعر: {e}")
        return float(price)
