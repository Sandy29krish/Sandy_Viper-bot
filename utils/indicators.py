"""
Technical indicators module for Sandy Viper Bot
Provides various technical analysis indicators
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional, Dict


class TechnicalIndicators:
    """Technical indicators calculator"""
    
    @staticmethod
    def sma(data: List[float], period: int) -> List[float]:
        """Simple Moving Average"""
        if len(data) < period:
            return []
        
        sma_values = []
        for i in range(period - 1, len(data)):
            avg = sum(data[i - period + 1:i + 1]) / period
            sma_values.append(avg)
        
        return sma_values
    
    @staticmethod
    def ema(data: List[float], period: int) -> List[float]:
        """Exponential Moving Average"""
        if len(data) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = []
        
        # First EMA is SMA
        first_ema = sum(data[:period]) / period
        ema_values.append(first_ema)
        
        # Calculate subsequent EMAs
        for i in range(period, len(data)):
            ema = (data[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    @staticmethod
    def rsi(data: List[float], period: int = 14) -> List[float]:
        """Relative Strength Index"""
        if len(data) < period + 1:
            return []
        
        gains = []
        losses = []
        
        # Calculate price changes
        for i in range(1, len(data)):
            change = data[i] - data[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        rsi_values = []
        
        # Calculate RSI for each period
        for i in range(period - 1, len(gains)):
            avg_gain = sum(gains[i - period + 1:i + 1]) / period
            avg_loss = sum(losses[i - period + 1:i + 1]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values
    
    @staticmethod
    def macd(data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """MACD (Moving Average Convergence Divergence)"""
        if len(data) < slow:
            return [], [], []
        
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        
        # Align the EMAs (slow EMA starts later)
        start_index = slow - fast
        ema_fast_aligned = ema_fast[start_index:]
        
        # Calculate MACD line
        macd_line = [fast_val - slow_val for fast_val, slow_val in zip(ema_fast_aligned, ema_slow)]
        
        # Calculate signal line (EMA of MACD)
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        
        # Calculate histogram
        histogram = []
        signal_start = len(macd_line) - len(signal_line)
        for i in range(len(signal_line)):
            hist = macd_line[signal_start + i] - signal_line[i]
            histogram.append(hist)
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data: List[float], period: int = 20, std_dev: float = 2) -> Tuple[List[float], List[float], List[float]]:
        """Bollinger Bands"""
        if len(data) < period:
            return [], [], []
        
        sma = TechnicalIndicators.sma(data, period)
        upper_bands = []
        lower_bands = []
        
        for i in range(len(sma)):
            data_slice = data[i:i + period]
            std = np.std(data_slice)
            upper_bands.append(sma[i] + (std_dev * std))
            lower_bands.append(sma[i] - (std_dev * std))
        
        return upper_bands, sma, lower_bands
    
    @staticmethod
    def stochastic(high: List[float], low: List[float], close: List[float], 
                  k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Stochastic Oscillator"""
        if len(high) < k_period or len(low) < k_period or len(close) < k_period:
            return [], []
        
        k_values = []
        
        for i in range(k_period - 1, len(close)):
            highest_high = max(high[i - k_period + 1:i + 1])
            lowest_low = min(low[i - k_period + 1:i + 1])
            
            if highest_high == lowest_low:
                k_percent = 50  # Avoid division by zero
            else:
                k_percent = ((close[i] - lowest_low) / (highest_high - lowest_low)) * 100
            
            k_values.append(k_percent)
        
        # Calculate %D (SMA of %K)
        d_values = TechnicalIndicators.sma(k_values, d_period)
        
        return k_values, d_values
    
    @staticmethod
    def atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        """Average True Range"""
        if len(high) < 2 or len(low) < 2 or len(close) < 2:
            return []
        
        true_ranges = []
        
        for i in range(1, len(high)):
            tr1 = high[i] - low[i]
            tr2 = abs(high[i] - close[i - 1])
            tr3 = abs(low[i] - close[i - 1])
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        return TechnicalIndicators.sma(true_ranges, period)
    
    @staticmethod
    def support_resistance(data: List[float], window: int = 5) -> Tuple[List[float], List[float]]:
        """Find support and resistance levels"""
        supports = []
        resistances = []
        
        for i in range(window, len(data) - window):
            # Check for local minima (support)
            is_support = all(data[i] <= data[i - j] for j in range(1, window + 1)) and \
                        all(data[i] <= data[i + j] for j in range(1, window + 1))
            
            # Check for local maxima (resistance)
            is_resistance = all(data[i] >= data[i - j] for j in range(1, window + 1)) and \
                           all(data[i] >= data[i + j] for j in range(1, window + 1))
            
            if is_support:
                supports.append(data[i])
            if is_resistance:
                resistances.append(data[i])
        
        return supports, resistances
    
    @staticmethod
    def pivot_points(high: float, low: float, close: float) -> Dict[str, float]:
        """Calculate pivot points"""
        pivot = (high + low + close) / 3
        
        return {
            'pivot': pivot,
            'r1': (2 * pivot) - low,
            'r2': pivot + (high - low),
            'r3': high + 2 * (pivot - low),
            's1': (2 * pivot) - high,
            's2': pivot - (high - low),
            's3': low - 2 * (high - pivot)
        }
    
    @staticmethod
    def fibonacci_retracement(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        
        return {
            '0%': high,
            '23.6%': high - (0.236 * diff),
            '38.2%': high - (0.382 * diff),
            '50%': high - (0.5 * diff),
            '61.8%': high - (0.618 * diff),
            '100%': low
        }
    
    @staticmethod
    def analyze_trend(data: List[float], period: int = 20) -> str:
        """Analyze overall trend"""
        if len(data) < period:
            return "INSUFFICIENT_DATA"
        
        recent_data = data[-period:]
        sma_short = TechnicalIndicators.sma(recent_data, period // 2)
        sma_long = TechnicalIndicators.sma(recent_data, period)
        
        if not sma_short or not sma_long:
            return "INSUFFICIENT_DATA"
        
        if sma_short[-1] > sma_long[-1]:
            return "UPTREND"
        elif sma_short[-1] < sma_long[-1]:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"


# Global indicators instance
indicators = TechnicalIndicators()
