#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
وحدة متخصصة للتعرف على الأنماط السعرية
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class PatternRecognizer:
    """فئة متخصصة للتعرف على الأنماط السعرية"""
    
    def __init__(self):
        """تهيئة محلل الأنماط"""
        logger.info("تهيئة محلل الأنماط السعرية")
    
    def identify_all_patterns(self, data: pd.DataFrame) -> List[str]:
        """
        التعرف على جميع الأنماط المدعومة في البيانات
        
        Parameters:
            data: إطار بيانات OHLCV
        
        Returns:
            List[str]: قائمة بالأنماط المكتشفة
        """
        if data is None or len(data) < 5:
            logger.warning("بيانات غير كافية للتعرف على الأنماط")
            return []
        
        patterns = []
        
        try:
            # أنماط الشموع الفردية
            patterns.extend(self.identify_candlestick_patterns(data))
            
            # أنماط الانعكاس
            patterns.extend(self.identify_reversal_patterns(data))
            
            # أنماط الاستمرارية
            patterns.extend(self.identify_continuation_patterns(data))
            
            return patterns
            
        except Exception as e:
            logger.error(f"خطأ أثناء التعرف على الأنماط: {str(e)}")
            return []
    
    def identify_candlestick_patterns(self, data: pd.DataFrame) -> List[str]:
        """
        التعرف على أنماط الشموع الفردية
        
        Parameters:
            data: إطار بيانات OHLCV
        
        Returns:
            List[str]: قائمة بأنماط الشموع المكتشفة
        """
        patterns = []
        
        try:
            # استخدام آخر 5 شموع للتحليل
            recent_data = data.tail(5).copy()
            
            # نمط المطرقة
            if self._is_hammer(recent_data.iloc[-1]):
                patterns.append("نمط المطرقة")
            
            # نمط المطرقة المقلوبة
            if self._is_inverted_hammer(recent_data.iloc[-1]):
                patterns.append("نمط المطرقة المقلوبة")
            
            # نمط دوجي
            if self._is_doji(recent_data.iloc[-1]):
                patterns.append("نمط دوجي")
            
            # نمط نجمة الطلاق
            if len(recent_data) >= 3 and self._is_shooting_star(recent_data.iloc[-1]):
                patterns.append("نمط نجمة الطلاق")
            
            # نمط ابتلاع
            if len(recent_data) >= 2:
                if self._is_bullish_engulfing(recent_data.iloc[-2], recent_data.iloc[-1]):
                    patterns.append("نمط ابتلاع صاعد")
                elif self._is_bearish_engulfing(recent_data.iloc[-2], recent_data.iloc[-1]):
                    patterns.append("نمط ابتلاع هابط")
            
            # نمط النجمة
            if len(recent_data) >= 3:
                if self._is_morning_star(recent_data.iloc[-3], recent_data.iloc[-2], recent_data.iloc[-1]):
                    patterns.append("نمط نجمة الصباح")
                elif self._is_evening_star(recent_data.iloc[-3], recent_data.iloc[-2], recent_data.iloc[-1]):
                    patterns.append("نمط نجمة المساء")
            
            return patterns
            
        except Exception as e:
            logger.error(f"خطأ أثناء التعرف على أنماط الشموع: {str(e)}")
            return []
    
    def identify_reversal_patterns(self, data: pd.DataFrame) -> List[str]:
        """
        التعرف على أنماط الانعكاس
        
        Parameters:
            data: إطار بيانات OHLCV
        
        Returns:
            List[str]: قائمة بأنماط الانعكاس المكتشفة
        """
        patterns = []
        
        try:
            # نحتاج إلى عدد كافي من البيانات للتعرف على الأنماط
            if len(data) < 20:
                return []
            
            # نمط الرأس والكتفين
            if self._is_head_and_shoulders(data):
                patterns.append("نمط الرأس والكتفين")
            
            # نمط الرأس والكتفين المقلوب
            if self._is_inverse_head_and_shoulders(data):
                patterns.append("نمط الرأس والكتفين المقلوب")
            
            # نمط القاع المزدوج
            if self._is_double_bottom(data):
                patterns.append("نمط القاع المزدوج")
            
            # نمط القمة المزدوجة
            if self._is_double_top(data):
                patterns.append("نمط القمة المزدوجة")
            
            # نمط القاع الثلاثي
            if self._is_triple_bottom(data):
                patterns.append("نمط القاع الثلاثي")
            
            # نمط القمة الثلاثية
            if self._is_triple_top(data):
                patterns.append("نمط القمة الثلاثية")
            
            return patterns
            
        except Exception as e:
            logger.error(f"خطأ أثناء التعرف على أنماط الانعكاس: {str(e)}")
            return []
    
    def identify_continuation_patterns(self, data: pd.DataFrame) -> List[str]:
        """
        التعرف على أنماط الاستمرارية
        
        Parameters:
            data: إطار بيانات OHLCV
        
        Returns:
            List[str]: قائمة بأنماط الاستمرارية المكتشفة
        """
        patterns = []
        
        try:
            # نحتاج إلى عدد كافي من البيانات للتعرف على الأنماط
            if len(data) < 20:
                return []
            
            # نمط العلم
            if self._is_flag(data):
                patterns.append("نمط العلم")
            
            # نمط الوتد
            if self._is_wedge(data):
                patterns.append("نمط الوتد")
            
            # نمط المثلث
            triangle_type = self._identify_triangle(data)
            if triangle_type:
                patterns.append(f"نمط المثلث {triangle_type}")
            
            # نمط المستطيل
            if self._is_rectangle(data):
                patterns.append("نمط المستطيل")
            
            return patterns
            
        except Exception as e:
            logger.error(f"خطأ أثناء التعرف على أنماط الاستمرارية: {str(e)}")
            return []
    
    # طرق مساعدة للتعرف على أنماط الشموع الفردية
    
    def _is_hammer(self, candle):
        """التحقق من نمط المطرقة"""
        body_size = abs(candle['Close'] - candle['Open'])
        total_range = candle['High'] - candle['Low']
        
        if total_range == 0:
            return False
            
        body_to_range_ratio = body_size / total_range if total_range > 0 else 0
        
        lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
        upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
        
        return (body_to_range_ratio < 0.3 and 
                lower_shadow > 2 * body_size and 
                upper_shadow < 0.1 * total_range)
    
    def _is_inverted_hammer(self, candle):
        """التحقق من نمط المطرقة المقلوبة"""
        body_size = abs(candle['Close'] - candle['Open'])
        total_range = candle['High'] - candle['Low']
        
        if total_range == 0:
            return False
            
        body_to_range_ratio = body_size / total_range
        
        lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
        upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
        
        return (body_to_range_ratio < 0.3 and 
                upper_shadow > 2 * body_size and 
                lower_shadow < 0.1 * total_range)
    
    def _is_doji(self, candle):
        """التحقق من نمط دوجي"""
        body_size = abs(candle['Close'] - candle['Open'])
        total_range = candle['High'] - candle['Low']
        
        if total_range == 0:
            return False
            
        return body_size <= 0.05 * total_range
    
    def _is_shooting_star(self, candle):
        """التحقق من نمط نجمة الطلاق"""
        body_size = abs(candle['Close'] - candle['Open'])
        total_range = candle['High'] - candle['Low']
        
        if total_range == 0:
            return False
            
        body_to_range_ratio = body_size / total_range
        
        lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
        upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
        
        return (candle['Close'] < candle['Open'] and  # هابطة
                body_to_range_ratio < 0.3 and 
                upper_shadow > 2 * body_size and 
                lower_shadow < 0.1 * total_range)
    
    def _is_bullish_engulfing(self, candle1, candle2):
        """التحقق من نمط الابتلاع الصاعد"""
        return (candle1['Close'] < candle1['Open'] and  # الشمعة الأولى هابطة
                candle2['Close'] > candle2['Open'] and  # الشمعة الثانية صاعدة
                candle2['Open'] <= candle1['Close'] and 
                candle2['Close'] >= candle1['Open'])
    
    def _is_bearish_engulfing(self, candle1, candle2):
        """التحقق من نمط الابتلاع الهابط"""
        return (candle1['Close'] > candle1['Open'] and  # الشمعة الأولى صاعدة
                candle2['Close'] < candle2['Open'] and  # الشمعة الثانية هابطة
                candle2['Open'] >= candle1['Close'] and 
                candle2['Close'] <= candle1['Open'])
    
    def _is_morning_star(self, candle1, candle2, candle3):
        """التحقق من نمط نجمة الصباح"""
        # تنفيذ منطق التحقق من نمط نجمة الصباح
        # (تفاصيل التنفيذ مماثلة لما في ملف technical.py)
        return False
    
    def _is_evening_star(self, candle1, candle2, candle3):
        """التحقق من نمط نجمة المساء"""
        # تنفيذ منطق التحقق من نمط نجمة المساء
        # (تفاصيل التنفيذ مماثلة لما في ملف technical.py)
        return False
    
    # طرق مساعدة للتعرف على أنماط الانعكاس والاستمرارية
    
    def _is_head_and_shoulders(self, data):
        """التحقق من نمط الرأس والكتفين"""
        # (تنفيذ مبسط للتوضيح)
        return False
    
    def _is_inverse_head_and_shoulders(self, data):
        """التحقق من نمط الرأس والكتفين المقلوب"""
        # (تنفيذ مبسط للتوضيح)
        return False
    
    def _is_double_bottom(self, data):
        """التحقق من نمط القاع المزدوج"""
        # (تنفيذ مبسط للتوضيح)
        return False
    
    def _is_double_top(self, data):
        """التحقق من نمط القمة المزدوجة"""
        # (تنفيذ مبسط للتوضيح)
        return False
    
    def _is_triple_bottom(self, data):
        """التحقق من نمط القاع الثلاثي"""
        # (تنفيذ مبسط للتوضيح)
        return False
    
    def _is_triple_top(self, data):
        """التحقق من نمط القمة الثلاثية"""
        # (تنفيذ مبسط للتوضيح)
        return False
    
    def _is_flag(self, data):
        """التحقق من نمط العلم"""
        # (تنفيذ مبسط للتوضيح)
        return False
    
    def _is_wedge(self, data):
        """التحقق من نمط الوتد"""
        # (تنفيذ مبسط للتوضيح)
        return False
    
    def _identify_triangle(self, data):
        """التعرف على نوع المثلث (صاعد، هابط، متماثل)"""
        # (تنفيذ مبسط للتوضيح)
        return None
    
    def _is_rectangle(self, data):
        """التحقق من نمط المستطيل"""
        # (تنفيذ مبسط للتوضيح)
        return False
