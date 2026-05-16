"""
Flexible Backtesting System with Adjustable Signal Thresholds
Allows testing with different signal strengths
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backtest_strategy import StrategyBacktester
from datetime import datetime, timedelta
import pandas as pd

class FlexibleBacktester(StrategyBacktester):
    """Backtester with adjustable signal thresholds"""
    
    def __init__(self, initial_capital=100000, position_size=0.1, 
                 buy_threshold=20, strong_buy_threshold=40):
        """
        Initialize with custom thresholds
        
        Args:
            initial_capital: Starting capital
            position_size: Fraction per trade
            buy_threshold: Minimum score for BUY signal (default: 20, original: 40)
            strong_buy_threshold: Minimum score for STRONG BUY (default: 40, original: 60)
        """
        super().__init__(initial_capital, position_size)
        self.buy_threshold = buy_threshold
        self.strong_buy_threshold = strong_buy_threshold
        print(f"\n📊 Signal Thresholds:")
        print(f"   STRONG BUY: Score ≥ {strong_buy_threshold}")
        print(f"   BUY:        Score ≥ {buy_threshold}")
        print(f"   HOLD:       Score ≥ 0")
        print(f"   SELL:       Score < 0")
    
    def calculate_signal_score(self, data, nifty_data, index):
        """Override to use custom thresholds"""
        score, _, details = super().calculate_signal_score(data, nifty_data, index)
        
        # Apply custom thresholds
        if score >= self.strong_buy_threshold:
            signal = "STRONG BUY"
        elif score >= self.buy_threshold:
            signal = "BUY"
        elif score >= 0:
            signal = "HOLD"
        elif score >= -40:
            signal = "SELL"
        else:
            signal = "STRONG SELL"
        
        return score, signal, details


def run_flexible_backtest():
    """Run backtest with flexible thresholds"""
    
    print("="*80)
    print("FLEXIBLE BACKTESTING SYSTEM")
    print("="*80)
    
    # Test stocks
    symbols = ['HDFCBANK', 'ICICIBANK', 'INFY', 'TCS', 'RELIANCE', 
               'ITC', 'ASIANPAINT', 'TATASTEEL', 'SAIL', 'ADANIENT']
    
    # Backtest period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 months
    
    print(f"\nPeriod: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Stocks: {len(symbols)}")
    
    # Try different threshold levels
    threshold_configs = [
        ("Conservative (Original)", 40, 60),
        ("Moderate", 20, 40),
        ("Aggressive", 10, 30),
    ]
    
    all_results = {}
    
    for config_name, buy_thresh, strong_buy_thresh in threshold_configs:
        print(f"\n{'='*80}")
        print(f"TESTING: {config_name}")
        print(f"{'='*80}")
        
        backtester = FlexibleBacktester(
            initial_capital=100000,
            position_size=0.5,  # 50% per trade
            buy_threshold=buy_thresh,
            strong_buy_threshold=strong_buy_thresh
        )
        
        results = backtester.backtest_portfolio(
            symbols=symbols[:5],  # Test first 5 stocks
            start_date=start_date,
            end_date=end_date,
            holding_days=5
        )
        
        if results:
            all_results[config_name] = results
    
    # Compare results
    if all_results:
        print(f"\n{'='*80}")
        print("COMPARISON OF THRESHOLD STRATEGIES")
        print(f"{'='*80}\n")
        
        comparison = []
        for config_name, results in all_results.items():
            comparison.append({
                'Strategy': config_name,
                'Total Trades': results['total_trades'],
                'Win Rate': f"{results['overall_win_rate']:.1f}%",
                'Avg Return': f"{results['avg_return_pct']:+.2f}%"
            })
        
        comp_df = pd.DataFrame(comparison)
        print(comp_df.to_string(index=False))
        
        print(f"\n{'='*80}")
        print("RECOMMENDATION")
        print(f"{'='*80}")
        print("\n✓ Use 'Moderate' threshold for balanced trading")
        print("✓ Use 'Conservative' for high-quality signals only")
        print("✓ Use 'Aggressive' for more frequent trading")
    else:
        print("\n⚠️  No successful backtests with any threshold")
        print("\nPossible reasons:")
        print("1. Market in strong downtrend during test period")
        print("2. Try longer backtest period (1 year)")
        print("3. Test during different market conditions")


if __name__ == "__main__":
    run_flexible_backtest()

# Made with Bob
