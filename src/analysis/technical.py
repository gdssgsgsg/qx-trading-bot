#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
وحدة التحليل الفني باستخدام pandas_ta بدلاً من TA-Lib
"""

import logging
import numpy as np
import pandas as pd
import pandas_ta as ta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

@dataclass
class TechnicalAnalysisResult:
    """فئة لتخزين نتائج التحليل الفني"""
    symbol: str
    timeframe: str
    trend: str
    strength: float
    support_levels: List[float]
    resistance_levels: List[float]
    patterns: List[str]
    signals: List[str]
    indicators: Dict[str, Dict]
    analysis_text: str

class TechnicalAnalyzer:
    """
    فئة التحليل الفني المحسّنة لـ Render
    تستخدم pandas_ta بدلاً من TA-Lib لتسهيل التثبيت وتوفير الموارد
    """
    
    def __init__(self):
        """تهيئة محلل التحليل الفني"""
        logger.info("تهيئة محلل التحليل الفني باستخدام pandas_ta")
    
    def analyze(self, data: pd.DataFrame, symbol: str, timeframe: str) -> Optional[TechnicalAnalysisResult]:
        """
        تحليل البيانات وإنتاج نتائج التحليل الفني
        
        Parameters:
            data: إطار بيانات يحتوي على البيانات التاريخية (OHLCV)
            symbol: رمز الزوج
            timeframe: الإطار الزمني
        
        Returns:
            TechnicalAnalysisResult: نتائج التحليل الفني
        """
        if data is None or len(data) < 20:  # تقليل الحد الأدنى من 30 إلى 20
            logger.error(f"بيانات غير كافية لإجراء التحليل الفني لـ {symbol}")
            return None
        
        logger.info(f"إجراء التحليل الفني لـ {symbol} على الإطار الزمني {timeframe}")
        
        try:
            # استخراج أعمدة OHLCV
            ohlc_data = data.copy()
            
            # التأكد من وجود الأعمدة المطلوبة
            required_columns = ['Open', 'High', 'Low', 'Close']
            for col in required_columns:
                if col not in ohlc_data.columns:
                    logger.error(f"عمود {col} غير موجود في البيانات")
                    return None
            
            # إضافة عمود الحجم إذا لم يكن موجوداً
            if 'Volume' not in ohlc_data.columns:
                ohlc_data['Volume'] = 0
            
            # حساب المؤشرات الفنية
            indicators = self._calculate_indicators(ohlc_data)
            
            # تحديد الاتجاه وقوته
            trend, strength = self._determine_trend(ohlc_data, indicators)
            
            # تحديد مستويات الدعم والمقاومة
            support_levels, resistance_levels = self._find_support_resistance(ohlc_data)
            
            # التعرف على الأنماط السعرية
            patterns = self._identify_patterns(ohlc_data)
            
            # توليد الإشارات
            signals = self._generate_signals(ohlc_data, indicators, patterns)
            
            # إنشاء نص التحليل
            analysis_text = self._create_analysis_text(
                symbol, timeframe, trend, strength, 
                support_levels, resistance_levels, 
                patterns, signals, indicators
            )
            
            # إنشاء وإرجاع نتيجة التحليل
            result = TechnicalAnalysisResult(
                symbol=symbol,
                timeframe=timeframe,
                trend=trend,
                strength=strength,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                patterns=patterns,
                signals=signals,
                indicators=indicators,
                analysis_text=analysis_text
            )
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ أثناء تحليل {symbol}: {str(e)}")
            return None
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """
        حساب المؤشرات الفنية المختلفة باستخدام pandas_ta
        
        Parameters:
            data: إطار بيانات OHLCV
        
        Returns:
            Dict: قاموس يحتوي على نتائج المؤشرات
        """
        try:
            # إنشاء نسخة لتجنب التعديل على الإطار الأصلي
            df = data.copy()
            
            # حساب المتوسطات المتحركة
            sma_20 = df.ta.sma(length=20).fillna(0)
            sma_50 = df.ta.sma(length=50).fillna(0)
            sma_200 = df.ta.sma(length=200).fillna(0)
            
            ema_20 = df.ta.ema(length=20).fillna(0)
            ema_50 = df.ta.ema(length=50).fillna(0)
            ema_200 = df.ta.ema(length=200).fillna(0)
            
            # حساب مؤشر القوة النسبية (RSI)
            rsi = df.ta.rsi(length=14).fillna(50)
            
            # حساب مؤشر MACD
            macd_result = df.ta.macd(fast=12, slow=26, signal=9)
            macd = macd_result[f"MACD_12_26_9"].fillna(0)
            macd_signal = macd_result[f"MACDs_12_26_9"].fillna(0)
            macd_hist = macd_result[f"MACDh_12_26_9"].fillna(0)
            
            # حساب مؤشر Stochastic
            stoch_result = df.ta.stoch(k=14, d=3, smooth_k=3)
            slowk = stoch_result[f"STOCHk_14_3_3"].fillna(50)
            slowd = stoch_result[f"STOCHd_14_3_3"].fillna(50)
            
            # حساب مؤشر Bollinger Bands
            bb_result = df.ta.bbands(length=20, std=2)
            upper_band = bb_result[f"BBU_20_2.0"].fillna(df['Close'] + df['Close'] * 0.02)
            middle_band = bb_result[f"BBM_20_2.0"].fillna(df['Close'])
            lower_band = bb_result[f"BBL_20_2.0"].fillna(df['Close'] - df['Close'] * 0.02)
            
            # حساب مؤشر ADX (متوسط المؤشر الاتجاهي)
            adx_result = df.ta.adx(length=14)
            adx = adx_result[f"ADX_14"].fillna(25)
            
            # تجميع المؤشرات في قاموس
            indicators = {
                'SMA': {
                    '20': sma_20,
                    '50': sma_50,
                    '200': sma_200,
                    'current': {
                        '20': sma_20.iloc[-1],
                        '50': sma_50.iloc[-1],
                        '200': sma_200.iloc[-1]
                    }
                },
                'EMA': {
                    '20': ema_20,
                    '50': ema_50,
                    '200': ema_200,
                    'current': {
                        '20': ema_20.iloc[-1],
                        '50': ema_50.iloc[-1],
                        '200': ema_200.iloc[-1]
                    }
                },
                'RSI': {
                    'values': rsi,
                    'current': rsi.iloc[-1]
                },
                'MACD': {
                    'line': macd,
                    'signal': macd_signal,
                    'histogram': macd_hist,
                    'current': {
                        'line': macd.iloc[-1],
                        'signal': macd_signal.iloc[-1],
                        'histogram': macd_hist.iloc[-1]
                    }
                },
                'Stochastic': {
                    'k': slowk,
                    'd': slowd,
                    'current': {
                        'k': slowk.iloc[-1],
                        'd': slowd.iloc[-1]
                    }
                },
                'Bollinger': {
                    'upper': upper_band,
                    'middle': middle_band,
                    'lower': lower_band,
                    'current': {
                        'upper': upper_band.iloc[-1],
                        'middle': middle_band.iloc[-1],
                        'lower': lower_band.iloc[-1]
                    }
                },
                'ADX': {
                    'values': adx,
                    'current': adx.iloc[-1]
                }
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"خطأ أثناء حساب المؤشرات الفنية: {str(e)}")
            # إرجاع قاموس مؤشرات فارغ في حالة الخطأ
            return self._create_empty_indicators()
    
    def _create_empty_indicators(self):
        """إنشاء قاموس مؤشرات فارغ في حالة الخطأ"""
        return {
            'SMA': {'current': {'20': 0, '50': 0, '200': 0}},
            'EMA': {'current': {'20': 0, '50': 0, '200': 0}},
            'RSI': {'current': 50},
            'MACD': {'current': {'line': 0, 'signal': 0, 'histogram': 0}},
            'Stochastic': {'current': {'k': 50, 'd': 50}},
            'Bollinger': {'current': {'upper': 0, 'middle': 0, 'lower': 0}},
            'ADX': {'current': 25}
        }
        
    def _determine_trend(self, data: pd.DataFrame, indicators: Dict) -> Tuple[str, float]:
        """
        تحديد الاتجاه العام وقوته
        
        Parameters:
            data: إطار بيانات OHLCV
            indicators: قاموس المؤشرات المحسوبة
        
        Returns:
            Tuple[str, float]: الاتجاه (صاعد، هابط، متذبذب) وقوته (0-1)
        """
        try:
            # استخراج الإغلاقات والمؤشرات الحالية
            close = data['Close'].values
            current_close = close[-1]
            
            sma_20 = indicators['SMA']['current']['20']
            sma_50 = indicators['SMA']['current']['50']
            sma_200 = indicators['SMA']['current']['200']
            
            ema_20 = indicators['EMA']['current']['20']
            ema_50 = indicators['EMA']['current']['50']
            
            rsi = indicators['RSI']['current']
            macd_hist = indicators['MACD']['current']['histogram']
            adx = indicators['ADX']['current']
            
            # تحديد الاتجاه باستخدام المتوسطات المتحركة
            trend_factors = []
            
            # عوامل المتوسطات المتحركة
            if current_close > sma_20:
                trend_factors.append(1)  # فوق المتوسط 20 = إيجابي
            else:
                trend_factors.append(-1)
            
            if current_close > sma_50:
                trend_factors.append(1)  # فوق المتوسط 50 = إيجابي
            else:
                trend_factors.append(-1)
            
            if current_close > sma_200:
                trend_factors.append(1)  # فوق المتوسط 200 = إيجابي
            else:
                trend_factors.append(-1)
            
            if sma_20 > sma_50:
                trend_factors.append(1)  # المتوسط 20 فوق المتوسط 50 = إيجابي
            else:
                trend_factors.append(-1)
                
            # عوامل مؤشرات الزخم
            if rsi > 50:
                trend_factors.append(1)  # RSI فوق 50 = إيجابي
            else:
                trend_factors.append(-1)
            
            if macd_hist > 0:
                trend_factors.append(1)  # هيستوجرام MACD موجب = إيجابي
            else:
                trend_factors.append(-1)
            
            # حساب متوسط العوامل لتحديد الاتجاه
            trend_score = sum(trend_factors) / len(trend_factors)
            
            # تحديد قوة الاتجاه باستخدام ADX
            trend_strength = min(adx / 100, 1.0)  # تطبيع ADX إلى نطاق 0-1
            
            # تحديد الاتجاه بناءً على النتيجة
            if trend_score > 0.3:
                trend = "صاعد"
            elif trend_score < -0.3:
                trend = "هابط"
            else:
                trend = "متذبذب"
            
            # تحديد قوة الاتجاه كقيمة مطلقة
            strength = abs(trend_score) * trend_strength
            
            # وصف قوة الاتجاه
            if strength > 0.7:
                trend += " قوي"
            elif strength > 0.4:
                trend += " متوسط القوة"
            else:
                trend += " ضعيف"
            
            return trend, strength
            
        except Exception as e:
            logger.error(f"خطأ في تحديد الاتجاه: {str(e)}")
            return "غير محدد", 0.0
    
    def _find_support_resistance(self, data: pd.DataFrame) -> Tuple[List[float], List[float]]:
        """
        تحديد مستويات الدعم والمقاومة
        
        Parameters:
            data: إطار بيانات OHLCV
        
        Returns:
            Tuple[List[float], List[float]]: قوائم مستويات الدعم والمقاومة
        """
        try:
            # استخراج الأسعار
            high = data['High'].values
            low = data['Low'].values
            close = data['Close'].values
            
            # آخر سعر
            last_price = close[-1]
            
            # تحديد نقاط المحور
            pivot_points = self._calculate_pivot_points(data)
            
            # تصنيف المستويات
            resistance_levels = [level for level in pivot_points if level > last_price]
            support_levels = [level for level in pivot_points if level < last_price]
            
            # ترتيب المستويات من الأقرب إلى الأبعد
            resistance_levels.sort()
            support_levels.sort(reverse=True)
            
            # الاحتفاظ بأهم 3 مستويات
            resistance_levels = resistance_levels[:3]
            support_levels = support_levels[:3]
            
            return support_levels, resistance_levels
            
        except Exception as e:
            logger.error(f"خطأ في تحديد مستويات الدعم والمقاومة: {str(e)}")
            return [], []
    
    def _calculate_pivot_points(self, data: pd.DataFrame) -> List[float]:
        """
        حساب نقاط المحور (Pivot Points)
        
        Parameters:
            data: إطار بيانات OHLCV
        
        Returns:
            List[float]: قائمة نقاط المحور
        """
        try:
            # استخدام آخر 20 شمعة لتحديد القمم والقيعان المحلية
            window = min(20, len(data))
            recent_data = data.tail(window)
            
            # حساب نقطة المحور الرئيسية
            high = recent_data['High'].max()
            low = recent_data['Low'].min()
            close = recent_data['Close'].iloc[-1]
            
            pivot = (high + low + close) / 3
            
            # حساب مستويات الدعم والمقاومة
            r1 = 2 * pivot - low
            r2 = pivot + (high - low)
            r3 = high + 2 * (pivot - low)
            
            s1 = 2 * pivot - high
            s2 = pivot - (high - low)
            s3 = low - 2 * (high - pivot)
            
            # جمع كل المستويات
            levels = [pivot, r1, r2, r3, s1, s2, s3]
            
            # تحديد القمم والقيعان المحلية
            for i in range(1, len(recent_data) - 1):
                # القمم المحلية
                if recent_data['High'].iloc[i] > recent_data['High'].iloc[i-1] and \
                   recent_data['High'].iloc[i] > recent_data['High'].iloc[i+1]:
                    levels.append(recent_data['High'].iloc[i])
                
                # القيعان المحلية
                if recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-1] and \
                   recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+1]:
                    levels.append(recent_data['Low'].iloc[i])
            
            return levels
            
        except Exception as e:
            logger.error(f"خطأ في حساب نقاط المحور: {str(e)}")
            return []
    
    def _identify_patterns(self, data: pd.DataFrame) -> List[str]:
        """
        التعرف على الأنماط السعرية
        
        Parameters:
            data: إطار بيانات OHLCV
        
        Returns:
            List[str]: قائمة الأنماط المكتشفة
        """
        patterns = []
        
        try:
            # استخراج آخر 10 شموع للتحليل
            recent_data = data.tail(10).copy()
            
            # فحص نمط المطرقة
            if self._is_hammer(recent_data.iloc[-1]):
                patterns.append("نمط المطرقة (Hammer)")
            
            # فحص نمط المطرقة المقلوبة
            if self._is_inverted_hammer(recent_data.iloc[-1]):
                patterns.append("نمط المطرقة المقلوبة (Inverted Hammer)")
            
            # فحص نمط الابتلاع
            if len(recent_data) >= 2 and self._is_engulfing(recent_data.iloc[-2], recent_data.iloc[-1]):
                if recent_data.iloc[-1]['Close'] > recent_data.iloc[-1]['Open']:
                    patterns.append("نمط الابتلاع الصاعد (Bullish Engulfing)")
                else:
                    patterns.append("نمط الابتلاع الهابط (Bearish Engulfing)")
            
            # فحص نمط دوجي
            if self._is_doji(recent_data.iloc[-1]):
                patterns.append("نمط دوجي (Doji)")
            
            # فحص نمط نجمة المساء
            if len(recent_data) >= 3 and self._is_evening_star(
                recent_data.iloc[-3], recent_data.iloc[-2], recent_data.iloc[-1]
            ):
                patterns.append("نمط نجمة المساء (Evening Star)")
            
            # فحص نمط نجمة الصباح
            if len(recent_data) >= 3 and self._is_morning_star(
                recent_data.iloc[-3], recent_data.iloc[-2], recent_data.iloc[-1]
            ):
                patterns.append("نمط نجمة الصباح (Morning Star)")
            
            return patterns
            
        except Exception as e:
            logger.error(f"خطأ في التعرف على الأنماط: {str(e)}")
            return []
    
    def _is_hammer(self, candle):
        """التحقق من نمط المطرقة"""
        body_size = abs(candle['Close'] - candle['Open'])
        total_range = candle['High'] - candle['Low']
        
        if body_size == 0:
            return False
            
        body_to_range_ratio = body_size / total_range if total_range > 0 else 0
        
        lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
        upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
        
        # نمط المطرقة: جسم صغير، ظل سفلي طويل، ظل علوي قصير أو غير موجود
        if (body_to_range_ratio < 0.3 and 
            lower_shadow > 2 * body_size and 
            upper_shadow < 0.1 * total_range):
            return True
        
        return False
    
    def _is_inverted_hammer(self, candle):
        """التحقق من نمط المطرقة المقلوبة"""
        body_size = abs(candle['Close'] - candle['Open'])
        total_range = candle['High'] - candle['Low']
        
        if body_size == 0 or total_range == 0:
            return False
            
        body_to_range_ratio = body_size / total_range
        
        lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
        upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
        
        # نمط المطرقة المقلوبة: جسم صغير، ظل علوي طويل، ظل سفلي قصير أو غير موجود
        if (body_to_range_ratio < 0.3 and 
            upper_shadow > 2 * body_size and 
            lower_shadow < 0.1 * total_range):
            return True
        
        return False
    
    def _is_engulfing(self, candle1, candle2):
        """التحقق من نمط الابتلاع"""
        # الابتلاع الصاعد: شمعة هابطة متبوعة بشمعة صاعدة تبتلع الشمعة السابقة
        if (candle1['Close'] < candle1['Open'] and  # الشمعة الأولى هابطة
            candle2['Close'] > candle2['Open'] and  # الشمعة الثانية صاعدة
            candle2['Open'] <= candle1['Close'] and 
            candle2['Close'] >= candle1['Open']):
            return True
        
        # الابتلاع الهابط: شمعة صاعدة متبوعة بشمعة هابطة تبتلع الشمعة السابقة
        if (candle1['Close'] > candle1['Open'] and  # الشمعة الأولى صاعدة
            candle2['Close'] < candle2['Open'] and  # الشمعة الثانية هابطة
            candle2['Open'] >= candle1['Close'] and 
            candle2['Close'] <= candle1['Open']):
            return True
        
        return False
    
    def _is_doji(self, candle):
        """التحقق من نمط دوجي"""
        body_size = abs(candle['Close'] - candle['Open'])
        total_range = candle['High'] - candle['Low']
        
        if total_range == 0:
            return False
            
        # دوجي: جسم صغير جداً مقارنة بالنطاق الكلي
        return body_size <= 0.05 * total_range
    
    def _is_evening_star(self, candle1, candle2, candle3):
        """التحقق من نمط نجمة المساء"""
        # الشمعة الأولى صاعدة كبيرة
        is_candle1_bullish = candle1['Close'] > candle1['Open']
        candle1_body_size = abs(candle1['Close'] - candle1['Open'])
        
        # الشمعة الثانية صغيرة (دوجي أو شبه دوجي)
        candle2_body_size = abs(candle2['Close'] - candle2['Open'])
        is_candle2_small = candle2_body_size < 0.5 * candle1_body_size
        
        # الشمعة الثالثة هابطة كبيرة
        is_candle3_bearish = candle3['Close'] < candle3['Open']
        
        # فجوة صعودية بين الشمعة الأولى والثانية
        gap_up = min(candle2['Open'], candle2['Close']) > candle1['Close']
        
        # فجوة هبوطية بين الشمعة الثانية والثالثة
        gap_down = max(candle2['Open'], candle2['Close']) < candle3['Open']
        
        return (is_candle1_bullish and is_candle2_small and 
                is_candle3_bearish and (gap_up or gap_down))
    
    def _is_morning_star(self, candle1, candle2, candle3):
        """التحقق من نمط نجمة الصباح"""
        # الشمعة الأولى هابطة كبيرة
        is_candle1_bearish = candle1['Close'] < candle1['Open']
        candle1_body_size = abs(candle1['Close'] - candle1['Open'])
        
        # الشمعة الثانية صغيرة (دوجي أو شبه دوجي)
        candle2_body_size = abs(candle2['Close'] - candle2['Open'])
        is_candle2_small = candle2_body_size < 0.5 * candle1_body_size
        
        # الشمعة الثالثة صاعدة كبيرة
        is_candle3_bullish = candle3['Close'] > candle3['Open']
        
        # فجوة هبوطية بين الشمعة الأولى والثانية
        gap_down = max(candle2['Open'], candle2['Close']) < candle1['Close']
        
        # فجوة صعودية بين الشمعة الثانية والثالثة
        gap_up = min(candle2['Open'], candle2['Close']) > candle3['Open']
        
        return (is_candle1_bearish and is_candle2_small and 
                is_candle3_bullish and (gap_down or gap_up))
    
    def _generate_signals(self, data: pd.DataFrame, indicators: Dict, patterns: List[str]) -> List[str]:
        """
        توليد إشارات التداول
        
        Parameters:
            data: إطار بيانات OHLCV
            indicators: قاموس المؤشرات
            patterns: قائمة الأنماط المكتشفة
        
        Returns:
            List[str]: قائمة إشارات التداول
        """
        signals = []
        
        try:
            # استخراج المؤشرات الحالية
            close = data['Close'].values[-1]
            rsi = indicators['RSI']['current']
            macd_line = indicators['MACD']['current']['line']
            macd_signal = indicators['MACD']['current']['signal']
            macd_hist = indicators['MACD']['current']['histogram']
            stoch_k = indicators['Stochastic']['current']['k']
            stoch_d = indicators['Stochastic']['current']['d']
            bb_upper = indicators['Bollinger']['current']['upper']
            bb_lower = indicators['Bollinger']['current']['lower']
            
            # فحص تشبع الشراء/البيع في RSI
            if rsi > 70:
                signals.append("تشبع شرائي في مؤشر القوة النسبية RSI")
            elif rsi < 30:
                signals.append("تشبع بيعي في مؤشر القوة النسبية RSI")
            
            # فحص إشارات MACD
            if macd_line > macd_signal and macd_hist > 0:
                # التحقق إذا كان تقاطع حديث
                if len(indicators['MACD']['histogram']) > 1 and indicators['MACD']['histogram'].iloc[-2] < 0:
                    signals.append("تقاطع إيجابي حديث في مؤشر MACD")
                else:
                    signals.append("تقاطع إيجابي في مؤشر MACD")
            elif macd_line < macd_signal and macd_hist < 0:
                # التحقق إذا كان تقاطع حديث
                if len(indicators['MACD']['histogram']) > 1 and indicators['MACD']['histogram'].iloc[-2] > 0:
                    signals.append("تقاطع سلبي حديث في مؤشر MACD")
                else:
                    signals.append("تقاطع سلبي في مؤشر MACD")
            
            # فحص إشارات Stochastic
            if stoch_k < 20 and stoch_d < 20:
                signals.append("تشبع بيعي في مؤشر Stochastic")
            elif stoch_k > 80 and stoch_d > 80:
                signals.append("تشبع شرائي في مؤشر Stochastic")
            
            # فحص تقاطعات Stochastic
            if len(indicators['Stochastic']['k']) > 1 and len(indicators['Stochastic']['d']) > 1:
                k_prev = indicators['Stochastic']['k'].iloc[-2]
                d_prev = indicators['Stochastic']['d'].iloc[-2]
                
                if stoch_k > stoch_d and k_prev < d_prev:
                    signals.append("تقاطع إيجابي في مؤشر Stochastic")
                elif stoch_k < stoch_d and k_prev > d_prev:
                    signals.append("تقاطع سلبي في مؤشر Stochastic")
            
            # فحص إشارات Bollinger Bands
            if close > bb_upper:
                signals.append("السعر فوق الحد العلوي لمؤشر Bollinger Bands")
            elif close < bb_lower:
                signals.append("السعر تحت الحد السفلي لمؤشر Bollinger Bands")
            
            # إضافة إشارات من الأنماط
            for pattern in patterns:
                if "صاعد" in pattern or "المطرقة" in pattern or "نجمة الصباح" in pattern:
                    signals.append(f"إشارة صعود من {pattern}")
                elif "هابط" in pattern or "نجمة المساء" in pattern:
                    signals.append(f"إشارة هبوط من {pattern}")
            
            return signals
            
        except Exception as e:
            logger.error(f"خطأ في توليد الإشارات: {str(e)}")
            return []
    
    def _create_analysis_text(self, symbol, timeframe, trend, strength, 
                             support_levels, resistance_levels, 
                             patterns, signals, indicators) -> str:
        """
        إنشاء نص التحليل الفني بصيغة مفهومة
        
        Returns:
            str: نص التحليل الفني
        """
        try:
            # بداية التحليل
            analysis = []
            analysis.append(f"التحليل الفني لـ {symbol} على الإطار الزمني {timeframe}:")
            analysis.append("")
            
            # وصف الاتجاه
            analysis.append(f"الاتجاه العام: {trend}")
            
            # وصف المؤشرات الرئيسية
            analysis.append("")
            analysis.append("المؤشرات الفنية:")
            
            rsi = indicators['RSI']['current']
            analysis.append(f"- مؤشر القوة النسبية (RSI): {rsi:.2f}")
            if rsi > 70:
                analysis.append("  (تشبع شرائي، احتمالية هبوط)")
            elif rsi < 30:
                analysis.append("  (تشبع بيعي، احتمالية صعود)")
            else:
                analysis.append(f"  (في المنطقة المحايدة)")
            
            macd = indicators['MACD']['current']['line']
            macd_signal = indicators['MACD']['current']['signal']
            macd_hist = indicators['MACD']['current']['histogram']
            analysis.append(f"- مؤشر MACD: {macd:.4f}, خط الإشارة: {macd_signal:.4f}, الهيستوجرام: {macd_hist:.4f}")
            if macd > macd_signal:
                analysis.append("  (تقاطع إيجابي، إشارة صعود)")
            else:
                analysis.append("  (تقاطع سلبي، إشارة هبوط)")
            
            # وصف مستويات الدعم والمقاومة
            analysis.append("")
            analysis.append("مستويات الدعم:")
            for i, level in enumerate(support_levels):
                analysis.append(f"- الدعم {i+1}: {level:.4f}")
            
            analysis.append("")
            analysis.append("مستويات المقاومة:")
            for i, level in enumerate(resistance_levels):
                analysis.append(f"- المقاومة {i+1}: {level:.4f}")
            
            # وصف الأنماط المكتشفة
            if patterns:
                analysis.append("")
                analysis.append("الأنماط السعرية المكتشفة:")
                for pattern in patterns:
                    analysis.append(f"- {pattern}")
            
            # الإشارات والتوصيات
            if signals:
                analysis.append("")
                analysis.append("الإشارات والتوصيات:")
                for signal in signals:
                    analysis.append(f"- {signal}")
            
            # استنتاج نهائي
            analysis.append("")
            analysis.append("الاستنتاج:")
            
            buy_signals = sum(1 for signal in signals if "صعود" in signal or "إيجابي" in signal or "تشبع بيعي" in signal)
            sell_signals = sum(1 for signal in signals if "هبوط" in signal or "سلبي" in signal or "تشبع شرائي" in signal)
            
            if buy_signals > sell_signals and "صاعد" in trend:
                analysis.append("التحليل يشير إلى اتجاه صاعد قوي مع تأكيد من عدة مؤشرات.")
                analysis.append("توصية: فرصة شراء محتملة مع وضع وقف خسارة تحت أقرب مستوى دعم.")
            elif sell_signals > buy_signals and "هابط" in trend:
                analysis.append("التحليل يشير إلى اتجاه هابط قوي مع تأكيد من عدة مؤشرات.")
                analysis.append("توصية: فرصة بيع محتملة مع وضع وقف خسارة فوق أقرب مستوى مقاومة.")
            else:
                analysis.append("المؤشرات مختلطة، الاتجاه العام غير واضح.")
                analysis.append("توصية: الانتظار حتى ظهور إشارات أكثر وضوحًا.")
            
            return "\n".join(analysis)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء نص التحليل: {str(e)}")
            return f"حدث خطأ أثناء إنشاء التحليل: {str(e)}"
