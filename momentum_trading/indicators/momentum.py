"""
Momentum Indicators
RSI, ROC, Stochastic, Williams %R, and other momentum indicators
"""

import pandas as pd
import numpy as np
from typing import Optional
import ta


class MomentumIndicators:
    """
    Calculate momentum-based technical indicators
    """
    
    @staticmethod
    def calculate_rsi(
        data: pd.DataFrame,
        period: int = 14,
        column: str = 'Close'
    ) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            data: DataFrame with price data
            period: RSI period (default: 14)
            column: Column to use for calculation
            
        Returns:
            Series with RSI values (0-100)
        """
        rsi = ta.momentum.RSIIndicator(
            close=data[column],
            window=period
        )
        return rsi.rsi()
    
    @staticmethod
    def calculate_roc(
        data: pd.DataFrame,
        period: int = 10,
        column: str = 'Close'
    ) -> pd.Series:
        """
        Calculate Rate of Change (ROC) / Momentum
        
        Args:
            data: DataFrame with price data
            period: ROC period (default: 10)
            column: Column to use
            
        Returns:
            Series with ROC values (percentage)
        """
        roc = ta.momentum.ROCIndicator(
            close=data[column],
            window=period
        )
        return roc.roc()
    
    @staticmethod
    def calculate_stochastic(
        data: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3,
        smooth_k: int = 3
    ) -> tuple:
        """
        Calculate Stochastic Oscillator (%K and %D)
        
        Args:
            data: DataFrame with OHLC data
            k_period: %K period
            d_period: %D period (signal line)
            smooth_k: Smoothing for %K
            
        Returns:
            Tuple of (%K, %D) Series
        """
        stoch = ta.momentum.StochasticOscillator(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            window=k_period,
            smooth_window=smooth_k
        )
        
        k = stoch.stoch()
        d = stoch.stoch_signal()
        
        return k, d
    
    @staticmethod
    def calculate_williams_r(
        data: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Williams %R
        
        Args:
            data: DataFrame with OHLC data
            period: Lookback period
            
        Returns:
            Series with Williams %R values (-100 to 0)
        """
        wr = ta.momentum.WilliamsRIndicator(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            lbp=period
        )
        return wr.williams_r()
    
    @staticmethod
    def calculate_macd(
        data: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        column: str = 'Close'
    ) -> tuple:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: DataFrame with price data
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
            column: Column to use
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        macd = ta.trend.MACD(
            close=data[column],
            window_fast=fast_period,
            window_slow=slow_period,
            window_sign=signal_period
        )
        
        macd_line = macd.macd()
        signal_line = macd.macd_signal()
        histogram = macd.macd_diff()
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_cci(
        data: pd.DataFrame,
        period: int = 20
    ) -> pd.Series:
        """
        Calculate Commodity Channel Index (CCI)
        
        Args:
            data: DataFrame with OHLC data
            period: CCI period
            
        Returns:
            Series with CCI values
        """
        cci = ta.trend.CCIIndicator(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            window=period
        )
        return cci.cci()
    
    @staticmethod
    def calculate_awesome_oscillator(
        data: pd.DataFrame,
        short_period: int = 5,
        long_period: int = 34
    ) -> pd.Series:
        """
        Calculate Awesome Oscillator (AO)
        
        Args:
            data: DataFrame with OHLC data
            short_period: Short period
            long_period: Long period
            
        Returns:
            Series with AO values
        """
        ao = ta.momentum.AwesomeOscillatorIndicator(
            high=data['High'],
            low=data['Low'],
            window1=short_period,
            window2=long_period
        )
        return ao.awesome_oscillator()
    
    @staticmethod
    def calculate_tsi(
        data: pd.DataFrame,
        slow_period: int = 25,
        fast_period: int = 13,
        column: str = 'Close'
    ) -> pd.Series:
        """
        Calculate True Strength Index (TSI)
        
        Args:
            data: DataFrame with price data
            slow_period: Slow period
            fast_period: Fast period
            column: Column to use
            
        Returns:
            Series with TSI values
        """
        tsi = ta.momentum.TSIIndicator(
            close=data[column],
            window_slow=slow_period,
            window_fast=fast_period
        )
        return tsi.tsi()
    
    @staticmethod
    def calculate_relative_strength(
        stock_data: pd.DataFrame,
        index_data: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Relative Strength vs Index
        
        Args:
            stock_data: Stock price data
            index_data: Index price data
            period: Period for smoothing
            
        Returns:
            Series with relative strength values
        """
        # Calculate returns
        stock_returns = stock_data['Close'].pct_change()
        index_returns = index_data['Close'].pct_change()
        
        # Calculate relative strength
        rs = (1 + stock_returns) / (1 + index_returns)
        
        # Smooth with moving average
        rs_smooth = rs.rolling(window=period).mean()
        
        return rs_smooth
    
    @staticmethod
    def calculate_momentum_score(
        data: pd.DataFrame,
        rsi_weight: float = 0.3,
        roc_weight: float = 0.3,
        macd_weight: float = 0.2,
        stoch_weight: float = 0.2
    ) -> pd.Series:
        """
        Calculate composite momentum score (0-100)
        
        Args:
            data: DataFrame with OHLC data
            rsi_weight: Weight for RSI
            roc_weight: Weight for ROC
            macd_weight: Weight for MACD
            stoch_weight: Weight for Stochastic
            
        Returns:
            Series with momentum scores (0-100)
        """
        # Calculate individual indicators
        rsi = MomentumIndicators.calculate_rsi(data)
        roc = MomentumIndicators.calculate_roc(data)
        macd_line, signal_line, _ = MomentumIndicators.calculate_macd(data)
        stoch_k, _ = MomentumIndicators.calculate_stochastic(data)
        
        # Normalize indicators to 0-100 scale
        rsi_norm = rsi  # Already 0-100
        
        # ROC: normalize to 0-100 (assuming -20% to +20% range)
        roc_norm = ((roc + 20) / 40 * 100).clip(0, 100)
        
        # MACD: positive = bullish, negative = bearish
        macd_signal = (macd_line > signal_line).astype(int) * 100
        
        # Stochastic: already 0-100
        stoch_norm = stoch_k
        
        # Calculate weighted score
        momentum_score = (
            rsi_norm * rsi_weight +
            roc_norm * roc_weight +
            macd_signal * macd_weight +
            stoch_norm * stoch_weight
        )
        
        return momentum_score
    
    @staticmethod
    def add_all_momentum_indicators(
        data: pd.DataFrame,
        rsi_period: int = 14,
        roc_period: int = 10,
        stoch_period: int = 14,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9
    ) -> pd.DataFrame:
        """
        Add all momentum indicators to DataFrame
        
        Args:
            data: DataFrame with OHLC data
            rsi_period: RSI period
            roc_period: ROC period
            stoch_period: Stochastic period
            macd_fast: MACD fast period
            macd_slow: MACD slow period
            macd_signal: MACD signal period
            
        Returns:
            DataFrame with all momentum indicators added
        """
        df = data.copy()
        
        # RSI
        df['RSI'] = MomentumIndicators.calculate_rsi(df, rsi_period)
        
        # ROC / Momentum
        df['ROC'] = MomentumIndicators.calculate_roc(df, roc_period)
        
        # Stochastic
        stoch_k, stoch_d = MomentumIndicators.calculate_stochastic(df, stoch_period)
        df['Stoch_K'] = stoch_k
        df['Stoch_D'] = stoch_d
        
        # Williams %R
        df['Williams_R'] = MomentumIndicators.calculate_williams_r(df)
        
        # MACD
        macd_line, signal_line, histogram = MomentumIndicators.calculate_macd(
            df, macd_fast, macd_slow, macd_signal
        )
        df['MACD'] = macd_line
        df['MACD_Signal'] = signal_line
        df['MACD_Hist'] = histogram
        
        # CCI
        df['CCI'] = MomentumIndicators.calculate_cci(df)
        
        # Awesome Oscillator
        df['AO'] = MomentumIndicators.calculate_awesome_oscillator(df)
        
        # TSI
        df['TSI'] = MomentumIndicators.calculate_tsi(df)
        
        # Momentum Score
        df['Momentum_Score'] = MomentumIndicators.calculate_momentum_score(df)
        
        return df


# Example usage
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    sample_data = pd.DataFrame({
        'Date': dates,
        'Open': 100 + np.random.randn(100).cumsum(),
        'High': 102 + np.random.randn(100).cumsum(),
        'Low': 98 + np.random.randn(100).cumsum(),
        'Close': 100 + np.random.randn(100).cumsum(),
        'Volume': np.random.randint(1000000, 5000000, 100)
    })
    
    print("="*60)
    print("Momentum Indicators Example")
    print("="*60)
    
    # Add all momentum indicators
    result = MomentumIndicators.add_all_momentum_indicators(sample_data)
    
    print(f"\nOriginal columns: {sample_data.columns.tolist()}")
    print(f"\nNew columns added: {[col for col in result.columns if col not in sample_data.columns]}")
    print(f"\nLatest values:")
    print(result[['Date', 'Close', 'RSI', 'ROC', 'MACD', 'Momentum_Score']].tail())

# Made with Bob
