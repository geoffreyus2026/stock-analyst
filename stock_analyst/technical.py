import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from .config import MARKET_BENCHMARK, RISK_FREE_RATE

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Technical analysis using price data and indicators"""
    
    def __init__(self):
        self.periods = {
            'short': 20,
            'medium': 50,
            'long': 200
        }
    
    def get_price_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate various moving averages"""
        mas = {}
        for name, period in self.periods.items():
            mas[f'MA_{period}'] = data['Close'].rolling(window=period).mean().iloc[-1]
        
        return mas
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def calculate_macd(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate MACD indicator"""
        exp1 = data['Close'].ewm(span=12).mean()
        exp2 = data['Close'].ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        return {
            'macd': macd.iloc[-1],
            'signal': signal.iloc[-1],
            'histogram': histogram.iloc[-1]
        }
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        return {
            'upper_band': upper_band.iloc[-1],
            'middle_band': sma.iloc[-1],
            'lower_band': lower_band.iloc[-1],
            'band_width': (upper_band.iloc[-1] - lower_band.iloc[-1]) / sma.iloc[-1]
        }
    
    def calculate_volume_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate volume-based indicators"""
        volume_sma = data['Volume'].rolling(window=20).mean()
        current_volume = data['Volume'].iloc[-1]
        
        on_balance_volume = (data['Close'].diff() > 0).astype(int) * data['Volume']
        obv = on_balance_volume.cumsum()
        
        return {
            'volume_ratio': current_volume / volume_sma.iloc[-1],
            'obv_trend': obv.iloc[-1] - obv.iloc[-20],
            'volume_sma': volume_sma.iloc[-1]
        }
    
    def calculate_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """Identify support and resistance levels"""
        highs = data['High'].rolling(window=window, center=True).max()
        lows = data['Low'].rolling(window=window, center=True).min()
        
        resistance = highs.max()
        support = lows.min()
        
        return {
            'support': support,
            'resistance': resistance,
            'current_price': data['Close'].iloc[-1],
            'distance_to_support': (data['Close'].iloc[-1] - support) / support,
            'distance_to_resistance': (resistance - data['Close'].iloc[-1]) / resistance
        }
    
    def calculate_volatility(self, data: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        """Calculate volatility metrics"""
        returns = data['Close'].pct_change()
        
        historical_vol = returns.rolling(window=period).std() * np.sqrt(252)
        current_vol = historical_vol.iloc[-1]
        
        atr = self._calculate_atr(data, period)
        
        return {
            'historical_volatility': current_vol,
            'atr': atr.iloc[-1],
            'volatility_percentile': (historical_vol <= current_vol).mean()
        }
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def get_technical_summary(self, symbol: str) -> Dict:
        """Get comprehensive technical analysis summary"""
        try:
            data = self.get_price_data(symbol)
            
            # Calculate all indicators
            moving_averages = self.calculate_moving_averages(data)
            rsi = self.calculate_rsi(data)
            macd = self.calculate_macd(data)
            bollinger = self.calculate_bollinger_bands(data)
            volume = self.calculate_volume_indicators(data)
            support_resistance = self.calculate_support_resistance(data)
            volatility = self.calculate_volatility(data)
            
            # Generate signals
            current_price = data['Close'].iloc[-1]
            
            # Trend signals
            trend_signal = "NEUTRAL"
            if current_price > moving_averages['MA_50'] > moving_averages['MA_200']:
                trend_signal = "BULLISH"
            elif current_price < moving_averages['MA_50'] < moving_averages['MA_200']:
                trend_signal = "BEARISH"
            
            # Momentum signals
            momentum_signal = "NEUTRAL"
            if rsi < 30:
                momentum_signal = "OVERSOLD"
            elif rsi > 70:
                momentum_signal = "OVERBOUGHT"
            
            # Volume signal
            volume_signal = "NORMAL"
            if volume['volume_ratio'] > 1.5:
                volume_signal = "HIGH"
            elif volume['volume_ratio'] < 0.7:
                volume_signal = "LOW"
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'moving_averages': moving_averages,
                'rsi': rsi,
                'macd': macd,
                'bollinger_bands': bollinger,
                'volume': volume,
                'support_resistance': support_resistance,
                'volatility': volatility,
                'signals': {
                    'trend': trend_signal,
                    'momentum': momentum_signal,
                    'volume': volume_signal
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in technical analysis for {symbol}: {e}")
            return {'error': str(e), 'symbol': symbol}