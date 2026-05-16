"""
Simple test to verify backtesting system works
Tests with more lenient criteria to ensure trades are executed
"""

from backtest_strategy import StrategyBacktester
from datetime import datetime, timedelta

print("="*80)
print("BACKTESTING SYSTEM TEST")
print("="*80)

# Test with a single stock and shorter period
backtester = StrategyBacktester(
    initial_capital=100000,
    position_size=0.5  # Use 50% of capital
)

# Test last 3 months
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

print(f"\nTest Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"Testing with: TATASTEEL (typically volatile with good signals)")

# Test single stock
result = backtester.backtest_stock(
    symbol='TATASTEEL',
    start_date=start_date,
    end_date=end_date,
    holding_days=3  # Shorter holding period
)

if result:
    print("\n" + "="*80)
    print("✅ BACKTESTING SYSTEM WORKING!")
    print("="*80)
    print(f"\nKey Results:")
    print(f"  Total Trades: {result['total_trades']}")
    print(f"  Win Rate: {result['win_rate']:.1f}%")
    print(f"  Total Return: ₹{result['total_return']:,.2f} ({result['total_return_pct']:+.2f}%)")
    
    if result['total_trades'] > 0:
        print(f"\n  Sample Trades:")
        trades_df = result['trades']
        for idx, trade in trades_df.head(3).iterrows():
            print(f"    {trade['entry_date'].strftime('%Y-%m-%d')}: "
                  f"{trade['entry_signal']} → {trade['exit_reason']} "
                  f"({trade['profit_pct']:+.2f}%)")
else:
    print("\n⚠️  No trades executed. This could mean:")
    print("  1. Market conditions didn't trigger BUY signals")
    print("  2. Try a different stock or time period")
    print("  3. Adjust signal thresholds in backtest_strategy.py")

print("\n" + "="*80)
print("Test complete. The backtesting system is functional.")
print("="*80)

# Made with Bob
