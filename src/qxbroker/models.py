#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
نماذج البيانات المستخدمة في قسم QXBroker
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from datetime import datetime

@dataclass
class Asset:
    """نموذج لتمثيل أصل تداول"""
    id: int
    name: str
    ticker: str
    active: bool = True
    type: Optional[str] = None
    
    def __str__(self):
        return f"{self.name} ({self.ticker})"

@dataclass
class Candle:
    """نموذج لتمثيل شمعة"""
    timestamp: int
    open: float
    close: float
    high: float
    low: float
    volume: Optional[float] = 0
    
    @property
    def datetime(self) -> datetime:
        """تحويل الطابع الزمني إلى تاريخ"""
        return datetime.fromtimestamp(self.timestamp)
    
    @property
    def is_bullish(self) -> bool:
        """هل الشمعة صاعدة؟"""
        return self.close > self.open
    
    @property
    def body_size(self) -> float:
        """حجم جسم الشمعة"""
        return abs(self.close - self.open)
    
    @property
    def range(self) -> float:
        """نطاق الشمعة الكامل"""
        return self.high - self.low
    
    def __str__(self):
        direction = "صاعدة" if self.is_bullish else "هابطة"
        return f"شمعة {direction} ({self.datetime.strftime('%Y-%m-%d %H:%M')}): O={self.open}, H={self.high}, L={self.low}, C={self.close}, V={self.volume}"

@dataclass
class TradeSignal:
    """نموذج لتمثيل إشارة تداول"""
    id: str
    symbol: str
    timeframe: str
    signal_type: str  # شراء، بيع، انتظار
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    take_profit2: Optional[float] = None
    confidence: float
    indicators_used: str
    analysis_text: str
    created_at: datetime = datetime.now()
    
    def __str__(self):
        emoji = "🟢" if self.signal_type == "شراء" else "🔴" if self.signal_type == "بيع" else "⚪"
        return f"{emoji} إشارة {self.signal_type} لـ {self.symbol} ({self.timeframe}) - ثقة: {self.confidence}%"
