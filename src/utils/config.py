#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إدارة الإعدادات والمتغيرات البيئية
"""

import os
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """فئة الإعدادات الرئيسية"""
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ADMIN_ID: str
    QX_USERNAME: str
    QX_PASSWORD: str
    DEBUG: bool = False
    
    # إعدادات الأزواج المدعومة
    SUPPORTED_PAIRS = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT",  # عملات مشفرة
        "EURUSD", "GBPUSD", "USDJPY",     # عملات أجنبية
        "XAUUSD"                          # ذهب
    ]
    
    # الأطر الزمنية المدعومة
    SUPPORTED_TIMEFRAMES = ["5m", "15m", "30m", "1h", "4h", "1d"]
    
    # الحد الأدنى لنسبة الثقة لإصدار إشارة
    MIN_CONFIDENCE = 70

def load_config():
    """
    تحميل الإعدادات من المتغيرات البيئية
    
    Returns:
        Config: كائن الإعدادات
    """
    try:
        # القراءة من المتغيرات البيئية
        telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        telegram_admin_id = os.environ.get('TELEGRAM_ADMIN_ID')
        qx_username = os.environ.get('QX_USERNAME')
        qx_password = os.environ.get('QX_PASSWORD')
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        # التحقق من وجود المتغيرات الإلزامية
        missing_vars = []
        if not telegram_bot_token:
            missing_vars.append('TELEGRAM_BOT_TOKEN')
        if not telegram_admin_id:
            missing_vars.append('TELEGRAM_ADMIN_ID')
        if not qx_username:
            missing_vars.append('QX_USERNAME')
        if not qx_password:
            missing_vars.append('QX_PASSWORD')
        
        if missing_vars:
            logger.error(f"متغيرات بيئية مفقودة: {', '.join(missing_vars)}")
            raise ValueError(f"متغيرات بيئية مفقودة: {', '.join(missing_vars)}")
        
        # إنشاء وإرجاع كائن الإعدادات
        return Config(
            TELEGRAM_BOT_TOKEN=telegram_bot_token,
            TELEGRAM_ADMIN_ID=telegram_admin_id,
            QX_USERNAME=qx_username,
            QX_PASSWORD=qx_password,
            DEBUG=debug
        )
        
    except Exception as e:
        logger.error(f"خطأ أثناء تحميل الإعدادات: {e}")
        raise
