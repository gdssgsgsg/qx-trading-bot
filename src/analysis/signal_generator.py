#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
مولد الإشارات المتكامل
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

import pandas as pd

from src.analysis.technical import TechnicalAnalyzer
from src.analysis.patterns import PatternRecognizer
from src.utils.config import load_config

logger = logging.getLogger(__name__)

class SignalGenerator:
    """
    فئة مولد الإشارات
    توفر إشارات تداول دقيقة بناءً على التحليل الفني وتحليل الأنماط
    """
    
    def __init__(self, qx_client):
        """
        تهيئة مولد الإشارات
        
        Parameters:
            qx_client: مثيل من QXClient للحصول على البيانات
        """
        self.qx_client = qx_client
        self.config = load_config()
        self.technical_analyzer = TechnicalAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
        self.signals_cache = {}  # تخزين مؤقت للإشارات
        
        logger.info("تم تهيئة مولد الإشارات")
    
    def generate_signal(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """
        توليد إشارة تداول للزوج والإطار الزمني المحدد
        
        Parameters:
            symbol: رمز الزوج
            timeframe: الإطار الزمني
        
        Returns:
            Dict: قاموس يحتوي على معلومات الإشارة أو None في حالة الفشل
        """
        # التحقق من التخزين المؤقت
        cache_key = f"{symbol}_{timeframe}"
        if cache_key in self.signals_cache:
            cache_time = self.signals_cache[cache_key]['timestamp']
            current_time = datetime.now().timestamp()
            
            # استخدام الإشارة المخزنة إذا كانت حديثة (أقل من 5 دقائق)
            if current_time - cache_time < 300:
                logger.info(f"استخدام إشارة مخزنة لـ {symbol} ({timeframe})")
                return self.signals_cache[cache_key]['signal']
        
        try:
            logger.info(f"توليد إشارة تداول لـ {symbol} على الإطار الزمني {timeframe}")
            
            # الحصول على البيانات التاريخية
            historical_data = self.qx_client.get_historical_data(symbol, timeframe, 50)
            if historical_data is None or len(historical_data) < 20:
                logger.error(f"بيانات غير كافية لتوليد إشارة لـ {symbol}")
                return None
            
            # الحصول على السعر الحالي
            current_price = self.qx_client.get_current_price(symbol)
            if current_price is None:
                logger.error(f"فشل الحصول على السعر الحالي لـ {symbol}")
                return None
            
            # إجراء التحليل الفني
            technical_result = self.technical_analyzer.analyze(historical_data, symbol, timeframe)
            if technical_result is None:
                logger.error(f"فشل التحليل الفني لـ {symbol}")
                return None
            
            # تحليل الأنماط السعرية
            patterns = self.pattern_recognizer.identify_all_patterns(historical_data)
            
            # دمج المؤشرات لتوليد الإشارة
            signal = self._generate_signal_from_analysis(
                symbol, timeframe, current_price, technical_result, patterns
            )
            
            # تخزين الإشارة في التخزين المؤقت
            if signal:
                self.signals_cache[cache_key] = {
                    'signal': signal,
                    'timestamp': datetime.now().timestamp()
                }
            
            return signal
            
        except Exception as e:
            logger.error(f"خطأ أثناء توليد إشارة لـ {symbol}: {str(e)}")
            return None
    
    def _generate_signal_from_analysis(self, symbol, timeframe, current_price, technical_result, patterns):
        """
        توليد إشارة بناءً على نتائج التحليل
        
        Parameters:
            symbol: رمز الزوج
            timeframe: الإطار الزمني
            current_price: السعر الحالي
            technical_result: نتيجة التحليل الفني
            patterns: الأنماط المكتشفة
        
        Returns:
            Dict: قاموس يحتوي على معلومات الإشارة أو None إذا لم تكن هناك إشارة قوية
        """
        # تحديد نوع الإشارة (شراء/بيع/انتظار) بناءً على التحليل
        signal_type = "انتظار"  # القيمة الافتراضية هي انتظار
        
        if "صاعد قوي" in technical_result.trend:
            signal_type = "شراء"
        elif "هابط قوي" in technical_result.trend:
            signal_type = "بيع"
        elif "صاعد متوسط" in technical_result.trend:
            # التحقق من وجود أنماط مؤكدة للاتجاه الصاعد
            buy_patterns = sum(1 for pattern in patterns if "صاعد" in pattern or "المطرقة" in pattern or "القاع" in pattern)
            if buy_patterns > 0:
                signal_type = "شراء"
        elif "هابط متوسط" in technical_result.trend:
            # التحقق من وجود أنماط مؤكدة للاتجاه الهابط
            sell_patterns = sum(1 for pattern in patterns if "هابط" in pattern or "نجمة المساء" in pattern or "القمة" in pattern)
            if sell_patterns > 0:
                signal_type = "بيع"
        
        # إذا كانت الإشارة هي انتظار، نرجع None
        if signal_type == "انتظار":
            return None
        
        # حساب نقاط الدخول والخروج
        entry_price = current_price
        
        # تحديد وقف الخسارة والأهداف
        if signal_type == "شراء":
            # وقف الخسارة تحت أقرب مستوى دعم
            stop_loss = min(technical_result.support_levels) if technical_result.support_levels else current_price * 0.97
            
            # الأهداف فوق مستويات المقاومة
            targets = []
            for level in sorted(technical_result.resistance_levels):
                if level > current_price:
                    targets.append(level)
            
            if not targets:
                # إذا لم تكن هناك مستويات مقاومة أعلى من السعر الحالي
                target1 = current_price * 1.02
                target2 = current_price * 1.03
                targets = [target1, target2]
            
        else:  # بيع
            # وقف الخسارة فوق أقرب مستوى مقاومة
            stop_loss = max(technical_result.resistance_levels) if technical_result.resistance_levels else current_price * 1.03
            
            # الأهداف تحت مستويات الدعم
            targets = []
            for level in sorted(technical_result.support_levels, reverse=True):
                if level < current_price:
                    targets.append(level)
            
            if not targets:
                # إذا لم تكن هناك مستويات دعم أقل من السعر الحالي
                target1 = current_price * 0.98
                target2 = current_price * 0.97
                targets = [target1, target2]
        
        # حساب نسبة الثقة
        confidence = self._calculate_confidence(
            technical_result, patterns, signal_type
        )
        
        # إذا كانت نسبة الثقة منخفضة، لا نصدر إشارة
        if confidence < self.config.MIN_CONFIDENCE:
            return None
        
        # تجميع الإشارة في قاموس
        signal = {
            "id": str(uuid.uuid4()),
            "الزوج": symbol,
            "الإطار_الزمني": timeframe,
            "نوع": signal_type,
            "الاتجاه": technical_result.trend,
            "نقطة_الدخول": self._format_price(entry_price),
            "وقف_الخسارة": self._format_price(stop_loss),
            "الهدف": self._format_price(targets[0] if targets else (entry_price * 1.02 if signal_type == "شراء" else entry_price * 0.98)),
            "الهدف_الثاني": self._format_price(targets[1] if len(targets) > 1 else (entry_price * 1.04 if signal_type == "شراء" else entry_price * 0.96)),
            "نسبة_الثقة": int(confidence),
            "المؤشرات": self._format_indicators(technical_result.indicators),
            "الأنماط": ", ".join(patterns) if patterns else "لا توجد أنماط مميزة",
            "التحليل": technical_result.analysis_text,
            "الوقت": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"تم توليد إشارة {signal_type} لـ {symbol} بنسبة ثقة {confidence:.1f}%")
        return signal
    
    def _calculate_confidence(self, technical_result, patterns, signal_type) -> float:
        """
        حساب نسبة الثقة في الإشارة
        
        Parameters:
            technical_result: نتيجة التحليل الفني
            patterns: الأنماط المكتشفة
            signal_type: نوع الإشارة (شراء/بيع)
        
        Returns:
            float: نسبة الثقة من 0 إلى 100
        """
        # بداية النتيجة بقيمة متوسطة
        confidence = 50.0
        
        # زيادة الثقة بناءً على قوة الاتجاه الفني
        confidence += technical_result.strength * 20
        
        # زيادة الثقة بناءً على عدد الإشارات المؤكدة
        buy_signals = sum(1 for signal in technical_result.signals if "صعود" in signal or "إيجابي" in signal or "تشبع بيعي" in signal)
        sell_signals = sum(1 for signal in technical_result.signals if "هبوط" in signal or "سلبي" in signal or "تشبع شرائي" in signal)
        
        if signal_type == "شراء" and buy_signals > 0:
            confidence += min(buy_signals * 5, 20)
        elif signal_type == "بيع" and sell_signals > 0:
            confidence += min(sell_signals * 5, 20)
        
        # خفض الثقة إذا كانت هناك إشارات متضاربة
        if signal_type == "شراء" and sell_signals > 0:
            confidence -= min(sell_signals * 3, 15)
        elif signal_type == "بيع" and buy_signals > 0:
            confidence -= min(buy_signals * 3, 15)
        
        # زيادة الثقة بناءً على وجود أنماط سعرية مؤكدة
        confirming_patterns = 0
        
        if signal_type == "شراء":
            confirming_patterns = sum(1 for pattern in patterns 
                                   if "صاعد" in pattern 
                                   or "المطرقة" in pattern 
                                   or "القاع" in pattern)
        else:  # بيع
            confirming_patterns = sum(1 for pattern in patterns 
                                   if "هابط" in pattern 
                                   or "نجمة المساء" in pattern 
                                   or "القمة" in pattern)
        
        confidence += min(confirming_patterns * 5, 15)
        
        # تحديد الحد الأقصى والأدنى للثقة
        confidence = max(min(confidence, 98), 0)
        
        return confidence
    
    def _format_indicators(self, indicators):
        """
        تنسيق المؤشرات المستخدمة في صيغة نصية
        
        Returns:
            str: وصف نصي للمؤشرات
        """
        indicator_texts = []
        
        # إضافة مؤشر RSI
        rsi = indicators['RSI']['current']
        rsi_text = f"RSI = {rsi:.1f}"
        if rsi > 70:
            rsi_text += " (تشبع شرائي)"
        elif rsi < 30:
            rsi_text += " (تشبع بيعي)"
        indicator_texts.append(rsi_text)
        
        # إضافة مؤشر MACD
        macd = indicators['MACD']['current']['line']
        macd_signal = indicators['MACD']['current']['signal']
        if macd > macd_signal:
            indicator_texts.append("تقاطع MACD إيجابي")
        else:
            indicator_texts.append("تقاطع MACD سلبي")
        
        # إضافة مؤشر المتوسطات المتحركة
        if indicators['SMA']['current']['20'] > indicators['SMA']['current']['50']:
            indicator_texts.append("المتوسط 20 فوق المتوسط 50")
        else:
            indicator_texts.append("المتوسط 20 تحت المتوسط 50")
        
        return "، ".join(indicator_texts)
    
    def _format_price(self, price):
        """
        تنسيق السعر بالدقة المناسبة
        
        Parameters:
            price: السعر
        
        Returns:
            float: السعر المنسق
        """
        # تحديد الدقة بناءً على قيمة السعر
        if price < 0.1:
            return round(price, 6)
        elif price < 1:
            return round(price, 5)
        elif price < 10:
            return round(price, 4)
        elif price < 100:
            return round(price, 3)
        elif price < 1000:
            return round(price, 2)
        else:
            return round(price, 1)
