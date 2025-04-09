#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
عميل QXBroker محسّن لـ Render
"""

import logging
import os
import time
import pandas as pd
from quotexpy.api import Quotex
import traceback
from functools import lru_cache

from src.utils.config import load_config

logger = logging.getLogger(__name__)

class QXClient:
    """
    فئة عميل QXBroker المحسنة للعمل مع Render
    تتضمن تحسينات لاستهلاك الموارد والتعامل مع الاتصالات المتقطعة
    """
    
    _instance = None
    
    def __new__(cls):
        """تطبيق نمط Singleton لتوفير الموارد"""
        if cls._instance is None:
            cls._instance = super(QXClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """تهيئة عميل QXBroker"""
        if self._initialized:
            return
            
        # تحميل الإعدادات
        config = load_config()
        self.username = config.QX_USERNAME
        self.password = config.QX_PASSWORD
        
        # تهيئة العميل
        self.client = None
        self.is_logged_in = False
        self.assets_info = {}
        self.cache = {}
        self.last_login_attempt = 0
        self.login_cooldown = 60  # ثواني قبل إعادة محاولة تسجيل الدخول
        self.cache_ttl = 300  # عمر التخزين المؤقت بالثواني (5 دقائق)
        
        self._initialized = True
        logger.info("تم تهيئة عميل QXBroker")

    def initialize(self):
        """تهيئة العميل وتسجيل الدخول"""
        try:
            logger.info("محاولة الاتصال بـ QXBroker...")
            
            # إنشاء عميل جديد إذا لم يكن موجوداً
            if self.client is None:
                self.client = Quotex()
            
            # محاولة الاتصال
            check_login = self.client.connect()
            if not check_login:
                logger.error("فشل الاتصال بـ QXBroker")
                self.is_logged_in = False
                return False
            
            # تسجيل الدخول فقط إذا لم نكن مسجلين بالفعل
            if not self.is_logged_in:
                # الانتظار إذا كانت آخر محاولة تسجيل دخول حديثة
                current_time = time.time()
                if current_time - self.last_login_attempt < self.login_cooldown:
                    time_to_wait = self.login_cooldown - (current_time - self.last_login_attempt)
                    logger.info(f"تم تقييد محاولات تسجيل الدخول. الانتظار لـ {time_to_wait:.0f} ثواني.")
                    return False
                
                # تحديث وقت آخر محاولة
                self.last_login_attempt = current_time
                
                # محاولة تسجيل الدخول
                logger.info(f"محاولة تسجيل الدخول باستخدام المستخدم: {self.username}")
                check_auth = self.client.login(self.username, self.password)
                
                if check_auth:
                    self.is_logged_in = True
                    logger.info("تم تسجيل الدخول بنجاح إلى QXBroker")
                    
                    # تحميل معلومات الأصول
                    self._load_assets_info()
                    return True
                else:
                    logger.error("فشل المصادقة مع QXBroker، تحقق من اسم المستخدم وكلمة المرور")
                    self.is_logged_in = False
                    return False
            else:
                # نحن مسجلون بالفعل
                return True
                
        except Exception as e:
            logger.error(f"خطأ أثناء تهيئة عميل QXBroker: {str(e)}")
            logger.debug(traceback.format_exc())
            self.is_logged_in = False
            return False
    
    def _load_assets_info(self):
        """تحميل معلومات الأصول من المنصة بطريقة موفرة للموارد"""
        try:
            # التحقق مما إذا كنا قمنا بتحميل المعلومات مؤخرًا
            current_time = time.time()
            if 'assets_last_loaded' in self.cache and (current_time - self.cache['assets_last_loaded']) < 3600:
                logger.debug("استخدام معلومات الأصول المخزنة مؤقتًا")
                return
                
            logger.info("جاري تحميل معلومات الأصول...")
            
            # الحصول على قائمة الأصول
            assets = self.client.get_all_assets()
            
            if not assets:
                logger.warning("لم يتم الحصول على أي معلومات للأصول")
                return
            
            # تخزين معلومات الأصول في قاموس للوصول السريع
            self.assets_info = {}
            for asset in assets:
                asset_id = asset.get('id')
                asset_name = asset.get('name', '').upper()
                
                if asset_id and asset_name:
                    self.assets_info[asset_name] = {
                        'id': asset_id,
                        'name': asset_name,
                        'ticker': asset.get('ticker', asset_name),
                        'active': asset.get('enabled', True)
                    }
            
            # تحديث وقت التحميل في التخزين المؤقت
            self.cache['assets_last_loaded'] = current_time
            
            logger.info(f"تم تحميل معلومات {len(self.assets_info)} أصل بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ أثناء تحميل معلومات الأصول: {str(e)}")
    
    def _ensure_logged_in(self):
        """التأكد من تسجيل الدخول قبل أي عملية"""
        if not self.is_logged_in:
            logger.info("إعادة تسجيل الدخول...")
            return self.initialize()
        return True
    
    @lru_cache(maxsize=32)
    def _get_asset_id(self, symbol):
        """
        الحصول على معرف الأصل من رمزه مع تخزين مؤقت لتحسين الأداء
        
        Parameters:
            symbol: رمز الزوج (مثل BTCUSDT)
        
        Returns:
            int: معرف الأصل أو None في حالة عدم العثور عليه
        """
        symbol_upper = symbol.upper()
        
        # التحقق من وجود الأصل في القاموس المخزن مسبقًا
        if symbol_upper in self.assets_info:
            return self.assets_info[symbol_upper]['id']
        
        # إذا لم يتم العثور على الأصل، نقوم بتحديث قائمة الأصول
        try:
            # تحديث معلومات الأصول
            self._load_assets_info()
            
            # التحقق مرة أخرى
            if symbol_upper in self.assets_info:
                return self.assets_info[symbol_upper]['id']
            
            # البحث بطريقة أخرى
            for asset_name, asset_info in self.assets_info.items():
                if asset_info['ticker'] == symbol_upper:
                    return asset_info['id']
            
            logger.warning(f"لم يتم العثور على الأصل: {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"خطأ أثناء البحث عن معرف الأصل لـ {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol):
        """
        الحصول على السعر الحالي للزوج المحدد مع آلية تعافي محسّنة
        
        Parameters:
            symbol: رمز الزوج (مثل BTCUSDT)
        
        Returns:
            float: السعر الحالي أو None في حالة الفشل
        """
        # التحقق من التخزين المؤقت أولاً
        cache_key = f"price_{symbol}"
        current_time = time.time()
        
        # استخدام السعر المخزن مؤقتًا إذا كان حديثًا (أقل من 30 ثانية)
        if cache_key in self.cache and (current_time - self.cache[cache_key]['timestamp']) < 30:
            logger.debug(f"استخدام السعر المخزن مؤقتًا لـ {symbol}")
            return self.cache[cache_key]['data']
        
        # التأكد من تسجيل الدخول
        if not self._ensure_logged_in():
            return None
        
        try:
            # الحصول على معرف الأصل
            asset_id = self._get_asset_id(symbol)
            if not asset_id:
                logger.error(f"لم يتم العثور على معرف الأصل لـ {symbol}")
                return None
            
            # الحصول على السعر الحالي
            price = self.client.get_price(asset_id)
            
            if price is not None:
                price = float(price)
                
                # تخزين السعر في التخزين المؤقت
                self.cache[cache_key] = {
                    'data': price,
                    'timestamp': current_time
                }
                
                return price
            else:
                logger.warning(f"تم إرجاع سعر فارغ لـ {symbol}")
                return None
            
        except Exception as e:
            logger.error(f"خطأ أثناء الحصول على سعر {symbol}: {str(e)}")
            self.is_logged_in = False  # إعادة ضبط حالة تسجيل الدخول
            return None
    
    def get_historical_data(self, symbol, timeframe, limit=50):
        """
        الحصول على البيانات التاريخية مع تحسينات للأداء وإدارة الموارد
        تم تقليل القيمة الافتراضية للحد من 100 إلى 50 لتوفير الموارد
        
        Parameters:
            symbol: رمز الزوج (مثل BTCUSDT)
            timeframe: الإطار الزمني (مثل 1h, 4h)
            limit: عدد الشموع المطلوبة
        
        Returns:
            DataFrame: إطار بيانات يحتوي على البيانات التاريخية أو None في حالة الفشل
        """
        # التحقق من التخزين المؤقت
        cache_key = f"{symbol}_{timeframe}_{limit}"
        current_time = time.time()
        
        # استخدام البيانات المخزنة مؤقتًا إذا كانت حديثة
        if cache_key in self.cache and (current_time - self.cache[cache_key]['timestamp']) < self.cache_ttl:
            logger.debug(f"استخدام البيانات المخزنة مؤقتًا لـ {symbol} ({timeframe})")
            return self.cache[cache_key]['data']
        
        # التأكد من تسجيل الدخول
        if not self._ensure_logged_in():
            return None
        
        try:
            # الحصول على معرف الأصل
            asset_id = self._get_asset_id(symbol)
            if not asset_id:
                logger.error(f"لم يتم العثور على معرف الأصل لـ {symbol}")
                return None
            
            # تحويل الإطار الزمني إلى قيمة بالثواني
            timeframe_seconds = self._convert_timeframe_to_seconds(timeframe)
            if not timeframe_seconds:
                logger.error(f"إطار زمني غير مدعوم: {timeframe}")
                return None
            
            # حساب الوقت البداية والنهاية
            end_time = int(current_time)
            start_time = end_time - (timeframe_seconds * limit)
            
            # الحصول على البيانات التاريخية
            logger.info(f"جلب البيانات التاريخية لـ {symbol} على الإطار الزمني {timeframe} (عدد {limit})")
            candles = self.client.get_candles(asset_id, timeframe_seconds, limit, start_time, end_time)
            
            if not candles:
                logger.warning(f"لم يتم الحصول على بيانات تاريخية لـ {symbol}")
                # استخدام البيانات القديمة من التخزين المؤقت إذا كانت متوفرة
                if cache_key in self.cache:
                    logger.warning(f"استخدام بيانات قديمة من التخزين المؤقت لـ {symbol}")
                    return self.cache[cache_key]['data']
                return None
            
            # تحويل البيانات إلى DataFrame
            df = pd.DataFrame(candles)
            
            # التأكد من وجود البيانات الصحيحة
            if len(df.columns) < 5:
                logger.error(f"تنسيق البيانات المستلمة غير صحيح: {df.columns}")
                return None
                
            # تسمية الأعمدة
            df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume'] if len(df.columns) >= 6 else ['Date', 'Open', 'Close', 'High', 'Low']
            
            # إضافة عمود الحجم إذا كان غير موجود
            if 'Volume' not in df.columns:
                df['Volume'] = 0
            
            # تحويل الطابع الزمني إلى تاريخ
            df['Date'] = pd.to_datetime(df['Date'], unit='s')
            
            # ترتيب البيانات من الأقدم إلى الأحدث
            df = df.sort_values('Date')
            
            # تحويل أعمدة الأسعار إلى أرقام float
            for col in ['Open', 'Close', 'High', 'Low']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # تخزين البيانات في التخزين المؤقت
            self.cache[cache_key] = {
                'data': df,
                'timestamp': current_time
            }
            
            logger.info(f"تم الحصول على {len(df)} صف من البيانات التاريخية لـ {symbol} ({timeframe})")
            return df
            
        except Exception as e:
            logger.error(f"خطأ أثناء الحصول على البيانات التاريخية لـ {symbol}: {str(e)}")
            self.is_logged_in = False  # إعادة ضبط حالة تسجيل الدخول
            return None
    
    def _convert_timeframe_to_seconds(self, timeframe):
        """
        تحويل الإطار الزمني إلى قيمة بالثواني
        
        Parameters:
            timeframe: الإطار الزمني (مثل 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
        
        Returns:
            int: الإطار الزمني بالثواني أو None إذا كان غير مدعوم
        """
        timeframe_mapping = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400,
            "1w": 604800
        }
        
        return timeframe_mapping.get(timeframe)
    
    def close(self):
        """إغلاق الاتصال وتنظيف الموارد"""
        if self.client:
            try:
                self.client.close()
                logger.info("تم إغلاق اتصال QXBroker بنجاح")
            except Exception as e:
                logger.error(f"خطأ أثناء إغلاق اتصال QXBroker: {str(e)}")
