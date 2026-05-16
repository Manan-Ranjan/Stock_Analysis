"""
Trend Indicators
SuperTrend, Moving Averages, ADX, and other trend indicators
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
import ta


class TrendIndicators:
    """
    Calculate trend-based technical indicators
    """
    
    @staticmethod
    def calculate_supertrend(
        data: pd.DataFrame,
        period: int = 10,
        multiplier: float = 3.0
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate SuperTrend indicator
        
        Args:
            data: DataFrame with OHLC data
            period: ATR period
            multiplier: ATR multiplier
            
        Returns:
            Tuple of (SuperTrend values, Trend direction: 1=up, -1=down)
        """
        # Calculate ATR
        atr = ta.volatility.AverageTrueRange(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            window=period
        ).average_true_range()
        
        # Calculate basic bands
        hl_avg = (data['High'] + data['Low']) / 2
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)
        
        # Initialize SuperTrend
        supertrend = pd.Series(index=data.index, dtype=float)
        direction = pd.Series(index=data.index, dtype=int)
        
        # First value
        supertrend.iloc[0] = lower_band.iloc[0]
        direction.iloc[0] = 1
        
        # Calculate SuperTrend
        for i in range(1, len(data)):
            # Update bands
            if data['Close'].iloc[i] > upper_band.iloc[i-1]:
                direction.iloc[i] = 1
            elif data['Close'].iloc[i] < lower_band.iloc[i-1]:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = direction.iloc[i-1]
                
                # Adjust bands
                if direction.iloc[i] == 1 and lower_band.iloc[i] < lower_band.iloc[i-1]:
                    lower_band.iloc[i] = lower_band.iloc[i-1]
                if direction.iloc[i] == -1 and upper_band.iloc[i] > upper_band.iloc[i-1]:
                    upper_band.iloc[i] = upper_band.iloc[i-1]
            
            # Set SuperTrend value
            if direction.iloc[i] == 1:
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                supertrend.iloc[i] = upper_band.iloc[i]
        
        return supertrend, direction
    
    @staticmethod
    def calculate_sma(
        data: pd.DataFrame,
        period: int = 20,
        column: str = 'Close'
    ) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA)
        
        Args:
            data: DataFrame with price data
            period: SMA period
            column: Column to use
            
        Returns:
            Series with SMA values
        """
        sma = ta.trend.SMAIndicator(
            close=data[column],
            window=period
        )
        return sma.sma_indicator()
    
    @staticmethod
    def calculate_ema(
        data: pd.DataFrame,
        period: int = 20,
        column: str = 'Close'
    ) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)
        
        Args:
            data: DataFrame with price data
            period: EMA period
            column: Column to use
            
        Returns:
            Series with EMA values
        """
        ema = ta.trend.EMAIndicator(
            close=data[column],
            window=period
        )
        return ema.ema_indicator()
    
    @staticmethod
    def calculate_wma(
        data: pd.DataFrame,
        period: int = 20,
        column: str = 'Close'
    ) -> pd.Series:
        """
        Calculate Weighted Moving Average (WMA)
        
        Args:
            data: DataFrame with price data
            period: WMA period
            column: Column to use
            
        Returns:
            Series with WMA values
        """
        wma = ta.trend.WMAIndicator(
            close=data[column],
            window=period
        )
        return wma.wma()
    
    @staticmethod
    def calculate_adx(
        data: pd.DataFrame,
        period: int = 14
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Average Directional Index (ADX)
        
        Args:
            data: DataFrame with OHLC data
            period: ADX period
            
        Returns:
            Tuple of (ADX, +DI, -DI)
        """
        adx_indicator = ta.trend.ADXIndicator(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            window=period
        )
        
        adx = adx_indicator.adx()
        plus_di = adx_indicator.adx_pos()
        minus_di = adx_indicator.adx_neg()
        
        return adx, plus_di, minus_di
    
    @staticmethod
    def calculate_aroon(
        data: pd.DataFrame,
        period: int = 25
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Aroon Indicator
        
        Args:
            data: DataFrame with OHLC data
            period: Aroon period
            
        Returns:
            Tuple of (Aroon Up, Aroon Down)
        """
        aroon = ta.trend.AroonIndicator(
            high=data['High'],
            low=data['Low'],
            window=period
        )
        
        aroon_up = aroon.aroon_up()
        aroon_down = aroon.aroon_down()
        
        return aroon_up, aroon_down
    
    @staticmethod
    def calculate_psar(
        data: pd.DataFrame,
        step: float = 0.02,
        max_step: float = 0.2
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Parabolic SAR
        
        Args:
            data: DataFrame with OHLC data
            step: Acceleration factor step
            max_step: Maximum acceleration factor
            
        Returns:
            Tuple of (PSAR values, Trend: 1=up, -1=down)
        """
        psar = ta.trend.PSARIndicator(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            step=step,
            max_step=max_step
        )
        
        psar_values = psar.psar()
        psar_up = psar.psar_up()
        psar_down = psar.psar_down()
        
        # Determine trend
        trend = pd.Series(index=data.index, dtype=int)
        trend[psar_up.notna()] = 1
        trend[psar_down.notna()] = -1
        
        return psar_values, trend
    
    @staticmethod
    def calculate_ichimoku(
        data: pd.DataFrame,
        conversion_period: int = 9,
        base_period: int = 26,
        span_b_period: int = 52,
        displacement: int = 26
    ) -> dict:
        """
        Calculate Ichimoku Cloud
        
        Args:
            data: DataFrame with OHLC data
            conversion_period: Tenkan-sen period
            base_period: Kijun-sen period
            span_b_period: Senkou Span B period
            displacement: Cloud displacement
            
        Returns:
            Dictionary with Ichimoku components
        """
        ichimoku = ta.trend.IchimokuIndicator(
            high=data['High'],
            low=data['Low'],
            window1=conversion_period,
            window2=base_period,
            window3=span_b_period
        )
        
        return {
            'tenkan_sen': ichimoku.ichimoku_conversion_line(),
            'kijun_sen': ichimoku.ichimoku_base_line(),
            'senkou_span_a': ichimoku.ichimoku_a(),
            'senkou_span_b': ichimoku.ichimoku_b()
        }
    
    @staticmethod
    def calculate_vortex(
        data: pd.DataFrame,
        period: int = 14
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Vortex Indicator
        
        Args:
            data: DataFrame with OHLC data
            period: Vortex period
            
        Returns:
            Tuple of (VI+, VI-)
        """
        vortex = ta.trend.VortexIndicator(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            window=period
        )
        
        vi_pos = vortex.vortex_indicator_pos()
        vi_neg = vortex.vortex_indicator_neg()
        
        return vi_pos, vi_neg
    
    @staticmethod
    def identify_trend(
        data: pd.DataFrame,
        short_ma: int = 20,
        long_ma: int = 50
    ) -> pd.Series:
        """
        Identify trend direction using moving averages
        
        Args:
            data: DataFrame with price data
            short_ma: Short MA period
            long_ma: Long MA period
            
        Returns:
            Series with trend: 1=uptrend, -1=downtrend, 0=sideways
        """
        sma_short = TrendIndicators.calculate_sma(data, short_ma)
        sma_long = TrendIndicators.calculate_sma(data, long_ma)
        
        trend = pd.Series(index=data.index, dtype=int)
        trend[sma_short > sma_long] = 1
        trend[sma_short < sma_long] = -1
        trend[sma_short == sma_long] = 0
        
        return trend
    
    @staticmethod
    def calculate_trend_strength(
        data: pd.DataFrame,
        adx_period: int = 14
    ) -> pd.Series:
        """
        Calculate trend strength using ADX
        
        Args:
            data: DataFrame with OHLC data
            adx_period: ADX period
            
        Returns:
            Series with trend strength classification
        """
        adx, _, _ = TrendIndicators.calculate_adx(data, adx_period)
        
        strength = pd.Series(index=data.index, dtype=str)
        strength[adx < 20] = 'Weak'
        strength[(adx >= 20) & (adx < 40)] = 'Moderate'
        strength[(adx >= 40) & (adx < 60)] = 'Strong'
        strength[adx >= 60] = 'Very Strong'
        
        return strength
    
    @staticmethod
    def add_all_trend_indicators(
        data: pd.DataFrame,
        supertrend_period: int = 10,
        supertrend_multiplier: float = 3.0,
        sma_periods: list = [20, 50, 200],
        ema_periods: list = [12, 26],
        adx_period: int = 14
    ) -> pd.DataFrame:
        """
        Add all trend indicators to DataFrame
        
        Args:
            data: DataFrame with OHLC data
            supertrend_period: SuperTrend period
            supertrend_multiplier: SuperTrend multiplier
            sma_periods: List of SMA periods
            ema_periods: List of EMA periods
            adx_period: ADX period
            
        Returns:
            DataFrame with all trend indicators added
        """
        df = data.copy()
        
        # SuperTrend
        supertrend, st_direction = TrendIndicators.calculate_supertrend(
            df, supertrend_period, supertrend_multiplier
        )
        df['SuperTrend'] = supertrend
        df['SuperTrend_Direction'] = st_direction
        
        # Moving Averages
        for period in sma_periods:
            df[f'SMA_{period}'] = TrendIndicators.calculate_sma(df, period)
        
        for period in ema_periods:
            df[f'EMA_{period}'] = TrendIndicators.calculate_ema(df, period)
        
        # ADX
        adx, plus_di, minus_di = TrendIndicators.calculate_adx(df, adx_period)
        df['ADX'] = adx
        df['Plus_DI'] = plus_di
        df['Minus_DI'] = minus_di
        
        # Aroon
        aroon_up, aroon_down = TrendIndicators.calculate_aroon(df)
        df['Aroon_Up'] = aroon_up
        df['Aroon_Down'] = aroon_down
        
        # Parabolic SAR
        psar, psar_trend = TrendIndicators.calculate_psar(df)
        df['PSAR'] = psar
        df['PSAR_Trend'] = psar_trend
        
        # Trend identification
        df['Trend'] = TrendIndicators.identify_trend(df)
        df['Trend_Strength'] = TrendIndicators.calculate_trend_strength(df)
        
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
    print("Trend Indicators Example")
    print("="*60)
    
    # Add all trend indicators
    result = TrendIndicators.add_all_trend_indicators(sample_data)
    
    print(f"\nOriginal columns: {sample_data.columns.tolist()}")
    print(f"\nNew columns added: {[col for col in result.columns if col not in sample_data.columns]}")
    print(f"\nLatest values:")
    print(result[['Date', 'Close', 'SuperTrend', 'SuperTrend_Direction', 'SMA_20', 'ADX', 'Trend']].tail())

# Made with Bob
