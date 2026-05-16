# Backtesting System for Portfolio Analysis Strategy

## Overview

This backtesting system allows you to test the effectiveness of your portfolio analysis strategy using historical data. It simulates real trading conditions and provides detailed performance metrics.

## Features

✅ **Historical Testing**: Test strategy on past data  
✅ **Realistic Simulation**: Includes entry/exit logic, stop loss, take profit  
✅ **Multiple Stocks**: Backtest entire portfolio at once  
✅ **Detailed Metrics**: Win rate, profit/loss, returns, and more  
✅ **Trade Log**: Complete record of all trades  
✅ **Risk Management**: Built-in stop loss (10%) and take profit (20%)  

## How It Works

### Strategy Logic

The backtester uses the same scoring system as the live analysis:

1. **Relative Strength vs NIFTY** (max ±30 points)
2. **Volume Expansion** (max 25 points)
3. **Momentum Indicators** (max 40 points)

**Signals:**
- **STRONG BUY**: Score ≥ 60
- **BUY**: Score ≥ 40
- **HOLD**: Score ≥ 0
- **SELL**: Score ≥ -40
- **STRONG SELL**: Score < -40

### Trading Rules

**Entry:**
- Enter position when signal is BUY or STRONG BUY
- Use 10% of capital per position (configurable)

**Exit:**
- Hold for 5 days (configurable)
- Stop loss at 10% loss
- Take profit at 20% gain
- Exit if signal turns to SELL/STRONG SELL

## Usage

### Basic Backtest

```python
from backtest_strategy import StrategyBacktester
from datetime import datetime, timedelta

# Initialize backtester
backtester = StrategyBacktester(
    initial_capital=100000,  # ₹1 lakh
    position_size=0.1        # 10% per trade
)

# Define backtest period
end_date = datetime.now()
start_date = end_date - timedelta(days=180)  # Last 6 months

# Backtest single stock
result = backtester.backtest_stock(
    symbol='HDFCBANK',
    start_date=start_date,
    end_date=end_date,
    holding_days=5
)
```

### Portfolio Backtest

```python
# Test multiple stocks
symbols = ['HDFCBANK', 'ICICIBANK', 'INFY', 'TCS', 'RELIANCE']

results = backtester.backtest_portfolio(
    symbols=symbols,
    start_date=start_date,
    end_date=end_date,
    holding_days=5
)
```

### Run Example

```bash
# Run the example backtest
python3 backtest_strategy.py
```

## Configuration Parameters

### StrategyBacktester

```python
StrategyBacktester(
    initial_capital=100000,  # Starting capital in INR
    position_size=0.1        # Fraction of capital per trade (0.1 = 10%)
)
```

### backtest_stock / backtest_portfolio

```python
backtest_stock(
    symbol='HDFCBANK',       # Stock symbol
    start_date=start_date,   # Start date (datetime)
    end_date=end_date,       # End date (datetime)
    holding_days=5           # Days to hold position
)
```

## Output & Results

### Console Output

```
==========================================================================================
Backtesting HDFCBANK
==========================================================================================

  ENTRY  2025-11-15 | ₹1650.50 | BUY          | Score:  45 | Shares: 60
  EXIT   2025-11-20 | ₹1685.25 | Holding period (5 days)  | P/L: +2.11%
  
  ENTRY  2025-12-03 | ₹1620.00 | STRONG BUY   | Score:  65 | Shares: 61
  EXIT   2025-12-08 | ₹1598.50 | Stop loss (10%)          | P/L: -1.33%

==========================================================================================
BACKTEST RESULTS - HDFCBANK
==========================================================================================
Total Trades:      15
Winning Trades:    9 (60.0%)
Losing Trades:     6
Avg Profit/Trade:  ₹1,250.50 (+1.25%)
Max Profit:        ₹8,500.00
Max Loss:          ₹-3,200.00
Total Return:      ₹18,757.50 (+18.76%)
Final Capital:     ₹118,757.50
```

### Portfolio Summary

```
==========================================================================================
PORTFOLIO SUMMARY
==========================================================================================
Symbol      Trades  Win Rate  Avg Profit  Total Return  Return %
HDFCBANK        15    60.0%    ₹1,251      ₹18,758      +18.76%
ICICIBANK       12    58.3%    ₹980        ₹11,760      +11.76%
INFY            18    55.6%    ₹750        ₹13,500      +13.50%
TCS             10    70.0%    ₹1,500      ₹15,000      +15.00%
RELIANCE        14    64.3%    ₹1,100      ₹15,400      +15.40%

==========================================================================================
OVERALL STATISTICS
==========================================================================================
Stocks Tested:     5
Total Trades:      69
Overall Win Rate:  61.2%
Avg Return/Stock:  +14.88%
Best Performer:    HDFCBANK (+18.76%)
Worst Performer:   ICICIBANK (+11.76%)
```

### Results Dictionary

```python
{
    'symbol': 'HDFCBANK',
    'total_trades': 15,
    'winning_trades': 9,
    'losing_trades': 6,
    'win_rate': 60.0,
    'total_return': 18757.50,
    'total_return_pct': 18.76,
    'avg_profit': 1250.50,
    'avg_profit_pct': 1.25,
    'max_profit': 8500.00,
    'max_loss': -3200.00,
    'final_capital': 118757.50,
    'trades': DataFrame  # Detailed trade log
}
```

### Trade Log DataFrame

Each trade includes:
- `entry_date`: When position was opened
- `entry_price`: Entry price
- `entry_signal`: BUY or STRONG BUY
- `entry_score`: Strategy score at entry
- `exit_date`: When position was closed
- `exit_price`: Exit price
- `exit_reason`: Why position was closed
- `shares`: Number of shares
- `profit`: Profit/loss in INR
- `profit_pct`: Profit/loss percentage
- `days_held`: Number of days held

## Interpreting Results

### Key Metrics

**Win Rate**: Percentage of profitable trades
- **Good**: > 55%
- **Excellent**: > 65%

**Average Return per Trade**:
- **Good**: > 1%
- **Excellent**: > 2%

**Total Return**:
- Compare against buy-and-hold strategy
- Compare against NIFTY 50 returns

### What to Look For

✅ **Positive Indicators:**
- Win rate > 55%
- Positive average return per trade
- Max profit > Max loss (in absolute terms)
- Consistent performance across stocks

⚠️ **Warning Signs:**
- Win rate < 50%
- Negative average return
- Large drawdowns
- High variability between stocks

## Optimization

### Adjusting Parameters

1. **Holding Period** (`holding_days`)
   - Shorter (3-5 days): More trades, faster exits
   - Longer (7-10 days): Fewer trades, ride trends

2. **Position Size** (`position_size`)
   - Smaller (5-10%): Lower risk, more diversification
   - Larger (20-30%): Higher risk, concentrated bets

3. **Stop Loss/Take Profit**
   - Modify in `backtest_stock()` method
   - Current: 10% stop loss, 20% take profit

### Testing Different Periods

```python
# Test different time periods
periods = [
    ('3 months', 90),
    ('6 months', 180),
    ('1 year', 365),
    ('2 years', 730)
]

for name, days in periods:
    start = datetime.now() - timedelta(days=days)
    end = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")
    
    results = backtester.backtest_portfolio(
        symbols=symbols,
        start_date=start,
        end_date=end,
        holding_days=5
    )
```

### Testing Different Holding Periods

```python
# Test different holding periods
for holding_days in [3, 5, 7, 10]:
    print(f"\nTesting {holding_days}-day holding period")
    
    results = backtester.backtest_portfolio(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        holding_days=holding_days
    )
```

## Advanced Usage

### Custom Exit Logic

Modify the `backtest_stock()` method to add custom exit conditions:

```python
# Example: Add trailing stop loss
if position is not None:
    # Update trailing stop
    if current_price > position.get('highest_price', position['entry_price']):
        position['highest_price'] = current_price
        position['trailing_stop'] = current_price * 0.95  # 5% trailing stop
    
    # Check trailing stop
    if current_price <= position.get('trailing_stop', 0):
        should_exit = True
        exit_reason = "Trailing stop (5%)"
```

### Sector-Based Analysis

```python
# Group stocks by sector
sectors = {
    'Banking': ['HDFCBANK', 'ICICIBANK', 'SBIN'],
    'IT': ['INFY', 'TCS'],
    'Energy': ['RELIANCE', 'IOC']
}

for sector, stocks in sectors.items():
    print(f"\n{'='*60}")
    print(f"SECTOR: {sector}")
    print(f"{'='*60}")
    
    results = backtester.backtest_portfolio(
        symbols=stocks,
        start_date=start_date,
        end_date=end_date,
        holding_days=5
    )
```

### Save Results

```python
from file_manager import DateStampedFileManager

# Save backtest results
file_manager = DateStampedFileManager(output_dir='backtest_results')

# Save summary
if results:
    csv_file = file_manager.get_csv_filename('backtest_summary')
    results['summary'].to_csv(csv_file, index=False)
    
    # Save detailed trades
    all_trades = pd.concat([r['trades'] for r in results['results']])
    trades_file = file_manager.get_csv_filename('backtest_trades')
    all_trades.to_csv(trades_file, index=False)
    
    print(f"Results saved to:")
    print(f"  Summary: {csv_file}")
    print(f"  Trades:  {trades_file}")
```

## Limitations & Considerations

### Data Limitations
- Uses Yahoo Finance data (may have gaps)
- No intraday data (daily close prices only)
- Limited historical data availability

### Simulation Assumptions
- Perfect execution at close prices
- No transaction costs or slippage
- No market impact from trades
- Assumes liquidity for all trades

### Strategy Limitations
- Based on technical indicators only
- No fundamental analysis
- No market regime consideration
- Fixed position sizing

## Best Practices

1. **Test Multiple Periods**: Don't rely on one time period
2. **Out-of-Sample Testing**: Test on recent data not used for development
3. **Walk-Forward Analysis**: Test strategy as it evolves over time
4. **Risk Management**: Always include stop losses
5. **Position Sizing**: Don't risk too much per trade
6. **Diversification**: Test across multiple stocks/sectors

## Troubleshooting

### Common Issues

**No trades executed:**
- Check if data is available for the period
- Verify signal generation logic
- Ensure sufficient capital for trades

**Poor performance:**
- Try different holding periods
- Adjust position sizing
- Test different time periods
- Check for overfitting

**Data errors:**
- Verify internet connection
- Check stock symbols are correct
- Ensure sufficient historical data

### Debug Mode

Add debug prints to see signal generation:

```python
# In calculate_signal_score method
print(f"Date: {current_date}, Score: {total_score}, Signal: {signal}")
print(f"  RS: {rs_score}, Vol: {volume_score}, Mom: {momentum_score}")
```

## Example Results Interpretation

### Good Strategy Example
```
Win Rate: 65%
Avg Return: +2.1% per trade
Total Return: +25% over 6 months
Max Drawdown: -5%
```
**Interpretation**: Strong strategy with consistent profits

### Poor Strategy Example
```
Win Rate: 45%
Avg Return: -0.5% per trade
Total Return: -8% over 6 months
Max Drawdown: -15%
```
**Interpretation**: Strategy needs improvement or different parameters

---

**Made with Bob** 🤖