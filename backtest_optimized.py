"""
Optimized Backtesting Strategy
Implements all improvements from STRATEGY_OPTIMIZATION_GUIDE.md
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backtest_strategy import StrategyBacktester
from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
import pandas as pd
from datetime import datetime, timedelta

class OptimizedBacktester(StrategyBacktester):
    """Enhanced backtester with optimizations"""
    
    def __init__(self, initial_capital=100000, base_position_size=0.1):
        super().__init__(initial_capital, base_position_size)
        self.min_score = 50  # Stricter entry (was 40)
        self.trailing_stop_pct = 0.05  # 5% trailing stop
        self.max_holding_days = 10  # Extended from 5
        
    def get_sector_strength(self, symbols, sector_map, days=30):
        """Calculate which sectors are performing well"""
        print("\n📊 Analyzing Sector Strength...")
        
        sector_scores = {}
        
        for symbol in symbols:
            if symbol not in sector_map:
                continue
                
            sector = sector_map[symbol]
            
            try:
                data = self.fetcher.fetch_stock_data(symbol, 'NSE', days=days)
                if data is not None and len(data) > 5:
                    # Calculate recent return
                    recent_return = (data.iloc[-1]['Close'] - data.iloc[-5]['Close']) / data.iloc[-5]['Close'] * 100
                    
                    if sector not in sector_scores:
                        sector_scores[sector] = []
                    sector_scores[sector].append(recent_return)
            except:
                continue
        
        # Average by sector
        sector_avg = {s: sum(scores)/len(scores) for s, scores in sector_scores.items() if scores}
        
        # Sort and display
        sorted_sectors = sorted(sector_avg.items(), key=lambda x: x[1], reverse=True)
        
        print("\nSector Performance (Last 30 days):")
        for sector, score in sorted_sectors:
            status = "🔥" if score > 5 else "📈" if score > 0 else "📉"
            print(f"  {status} {sector:20} {score:+6.2f}%")
        
        # Return top 3 sectors
        top_sectors = [s[0] for s in sorted_sectors[:3]]
        print(f"\n✓ Trading only top 3 sectors: {', '.join(top_sectors)}")
        
        return top_sectors
    
    def get_top_performers(self, symbols, lookback_days=30):
        """Identify stocks with best recent momentum"""
        print(f"\n📈 Identifying Top Performers (Last {lookback_days} days)...")
        
        performance = {}
        
        for symbol in symbols:
            try:
                data = self.fetcher.fetch_stock_data(symbol, 'NSE', days=lookback_days)
                if data is not None and len(data) > 5:
                    returns = (data.iloc[-1]['Close'] - data.iloc[-5]['Close']) / data.iloc[-5]['Close'] * 100
                    performance[symbol] = returns
            except:
                continue
        
        # Sort by performance
        sorted_stocks = sorted(performance.items(), key=lambda x: x[1], reverse=True)
        
        # Display all
        print("\nStock Performance:")
        for symbol, perf in sorted_stocks:
            status = "🟢" if perf > 5 else "🟡" if perf > 0 else "🔴"
            print(f"  {status} {symbol:12} {perf:+6.2f}%")
        
        # Return top 50%
        top_half = max(1, len(sorted_stocks) // 2)
        top_stocks = [s[0] for s in sorted_stocks[:top_half]]
        
        print(f"\n✓ Trading top {len(top_stocks)} performers: {', '.join(top_stocks)}")
        
        return top_stocks
    
    def is_market_bullish(self, nifty_data, index):
        """Check if overall market is in uptrend"""
        
        if nifty_data is None or len(nifty_data) <= index or index < 20:
            return True  # Default to allow trading
        
        try:
            current = nifty_data.iloc[index]
            prev_20 = nifty_data.iloc[index-20]
            
            # Market return
            nifty_return = (current['Close'] - prev_20['Close']) / prev_20['Close'] * 100
            
            # Check if above MA
            nifty_above_ma = current['Close'] > current.get('SMA_50', current['Close'])
            
            return nifty_return > 0 and nifty_above_ma
        except:
            return True
    
    def calculate_position_size_dynamic(self, capital, score):
        """Dynamic position sizing based on signal strength"""
        
        if score >= 70:
            return capital * 0.15  # 15% for very strong signals
        elif score >= 60:
            return capital * 0.12  # 12% for strong signals
        elif score >= 50:
            return capital * 0.10  # 10% for good signals
        else:
            return capital * 0.07  # 7% for moderate signals
    
    def backtest_stock_optimized(self, symbol, start_date, end_date, sector_map=None):
        """Optimized backtest with all improvements"""
        
        print(f"\n{'='*60}")
        print(f"Backtesting {symbol} (OPTIMIZED)")
        print(f"{'='*60}")
        
        # Fetch data
        days_needed = (end_date - start_date).days + 60
        data = self.fetcher.fetch_stock_data(symbol, exchange='NSE', days=days_needed)
        
        if data is None or data.empty:
            print(f"❌ No data for {symbol}")
            return None
        
        # Add indicators
        data = MomentumIndicators.add_all_momentum_indicators(data)
        from momentum_trading.indicators.trend import TrendIndicators
        data = TrendIndicators.add_all_trend_indicators(data)
        
        # Fetch NIFTY
        nifty_data = None
        for nifty_symbol in ['^NSEI', 'NIFTY']:
            try:
                nifty_data = self.fetcher.fetch_stock_data(nifty_symbol, exchange='', days=days_needed)
                if nifty_data is not None and not nifty_data.empty:
                    nifty_data = MomentumIndicators.add_all_momentum_indicators(nifty_data)
                    break
            except:
                continue
        
        # Reset index
        if not isinstance(data.index, pd.DatetimeIndex):
            data = data.reset_index()
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date'])
                data = data.set_index('Date')
        
        # Simulate trading
        trades = []
        position = None
        capital = self.initial_capital
        
        for i in range(20, len(data)):
            current_date = data.index[i]
            if not isinstance(current_date, pd.Timestamp):
                current_date = pd.to_datetime(current_date)
            
            if current_date < start_date or current_date > end_date:
                continue
            
            # Calculate signal
            score, signal, details = self.calculate_signal_score(data, nifty_data, i)
            current_price = details['close']
            
            # Check market condition
            market_bullish = self.is_market_bullish(nifty_data, i)
            
            # Manage existing position
            if position is not None:
                days_held = (current_date - position['entry_date']).days
                
                # Update trailing stop
                if 'highest_price' not in position:
                    position['highest_price'] = position['entry_price']
                
                if current_price > position['highest_price']:
                    position['highest_price'] = current_price
                    position['trailing_stop'] = current_price * (1 - self.trailing_stop_pct)
                
                # Exit conditions
                should_exit = False
                exit_reason = ""
                
                # 1. Trailing stop
                if current_price <= position.get('trailing_stop', 0):
                    should_exit = True
                    exit_reason = "Trailing stop (5%)"
                
                # 2. Hard stop loss
                elif current_price <= position['entry_price'] * 0.90:
                    should_exit = True
                    exit_reason = "Stop loss (10%)"
                
                # 3. Take profit
                elif current_price >= position['entry_price'] * 1.25:
                    should_exit = True
                    exit_reason = "Take profit (25%)"
                
                # 4. Max holding period
                elif days_held >= self.max_holding_days:
                    should_exit = True
                    exit_reason = f"Max holding ({self.max_holding_days} days)"
                
                # 5. Signal turns bearish
                elif signal in ["SELL", "STRONG SELL"]:
                    should_exit = True
                    exit_reason = f"Signal: {signal}"
                
                # 6. Market turns bearish
                elif not market_bullish:
                    should_exit = True
                    exit_reason = "Market bearish"
                
                if should_exit:
                    exit_value = position['shares'] * current_price
                    profit = exit_value - position['entry_value']
                    profit_pct = (profit / position['entry_value']) * 100
                    
                    trade = {
                        'symbol': symbol,
                        'entry_date': position['entry_date'],
                        'entry_price': position['entry_price'],
                        'entry_signal': position['entry_signal'],
                        'entry_score': position['entry_score'],
                        'exit_date': current_date,
                        'exit_price': current_price,
                        'exit_reason': exit_reason,
                        'shares': position['shares'],
                        'profit': profit,
                        'profit_pct': profit_pct,
                        'days_held': days_held
                    }
                    
                    trades.append(trade)
                    capital += exit_value
                    position = None
                    
                    date_str = pd.to_datetime(current_date).strftime('%Y-%m-%d')
                    print(f"  {'EXIT':<6} {date_str} | "
                          f"₹{current_price:8.2f} | {exit_reason:<25} | "
                          f"P/L: {profit_pct:+6.2f}%")
            
            # Check for new entry (OPTIMIZED CRITERIA)
            elif position is None:
                # Must meet stricter criteria
                if (score >= self.min_score and 
                    signal in ["BUY", "STRONG BUY"] and
                    market_bullish and
                    details['rs_value'] > 0 and  # Positive relative strength
                    details['rsi'] < 70):  # Not overbought
                    
                    # Dynamic position sizing
                    position_value = self.calculate_position_size_dynamic(capital, score)
                    shares = int(position_value / current_price)
                    
                    if shares > 0:
                        entry_value = shares * current_price
                        
                        position = {
                            'entry_date': current_date,
                            'entry_price': current_price,
                            'entry_signal': signal,
                            'entry_score': score,
                            'shares': shares,
                            'entry_value': entry_value,
                            'highest_price': current_price,
                            'trailing_stop': current_price * (1 - self.trailing_stop_pct)
                        }
                        
                        capital -= entry_value
                        
                        date_str = pd.to_datetime(current_date).strftime('%Y-%m-%d')
                        print(f"  {'ENTRY':<6} {date_str} | "
                              f"₹{current_price:8.2f} | {signal:<12} | "
                              f"Score: {score:3d} | Shares: {shares}")
        
        # Close any open position
        if position is not None:
            final_price = data.iloc[-1]['Close']
            exit_value = position['shares'] * final_price
            profit = exit_value - position['entry_value']
            profit_pct = (profit / position['entry_value']) * 100
            
            trade = {
                'symbol': symbol,
                'entry_date': position['entry_date'],
                'entry_price': position['entry_price'],
                'entry_signal': position['entry_signal'],
                'entry_score': position['entry_score'],
                'exit_date': data.index[-1],
                'exit_price': final_price,
                'exit_reason': 'End of backtest',
                'shares': position['shares'],
                'profit': profit,
                'profit_pct': profit_pct,
                'days_held': (data.index[-1] - position['entry_date']).days
            }
            
            trades.append(trade)
            capital += exit_value
        
        # Calculate results
        if not trades:
            print(f"\n⚠️  No trades executed for {symbol}")
            return None
        
        trades_df = pd.DataFrame(trades)
        
        total_return = capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        winning_trades = trades_df[trades_df['profit'] > 0]
        losing_trades = trades_df[trades_df['profit'] < 0]
        
        win_rate = (len(winning_trades) / len(trades_df)) * 100 if len(trades_df) > 0 else 0
        
        results = {
            'symbol': symbol,
            'total_trades': len(trades_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'avg_profit': trades_df['profit'].mean(),
            'avg_profit_pct': trades_df['profit_pct'].mean(),
            'max_profit': trades_df['profit'].max(),
            'max_loss': trades_df['profit'].min(),
            'final_capital': capital,
            'trades': trades_df
        }
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"OPTIMIZED RESULTS - {symbol}")
        print(f"{'='*60}")
        print(f"Total Trades:      {len(trades_df)}")
        print(f"Winning Trades:    {len(winning_trades)} ({win_rate:.1f}%)")
        print(f"Avg Profit/Trade:  ₹{results['avg_profit']:,.2f} ({results['avg_profit_pct']:+.2f}%)")
        print(f"Total Return:      ₹{total_return:,.2f} ({total_return_pct:+.2f}%)")
        
        return results


def run_comparison():
    """Compare baseline vs optimized strategy"""
    
    print("="*80)
    print("STRATEGY COMPARISON: BASELINE vs OPTIMIZED")
    print("="*80)
    
    # Test stocks with sector mapping
    sector_map = {
        'HDFCBANK': 'Banking',
        'ICICIBANK': 'Banking',
        'INFY': 'IT',
        'TCS': 'IT',
        'RELIANCE': 'Energy',
        'ITC': 'FMCG',
        'ASIANPAINT': 'FMCG',
        'TATASTEEL': 'Metals',
        'SAIL': 'Metals',
        'ADANIENT': 'Diversified'
    }
    
    symbols = list(sector_map.keys())
    
    # Backtest period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    print(f"\nPeriod: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Initialize optimized backtester
    optimized = OptimizedBacktester(initial_capital=100000, base_position_size=0.1)
    
    # Get strong sectors
    strong_sectors = optimized.get_sector_strength(symbols, sector_map)
    
    # Get top performers
    top_performers = optimized.get_top_performers(symbols)
    
    # Filter symbols (must be in both strong sector AND top performers)
    filtered_symbols = [s for s in symbols 
                       if sector_map[s] in strong_sectors and s in top_performers]
    
    print(f"\n✓ Final selection: {len(filtered_symbols)} stocks")
    print(f"  {', '.join(filtered_symbols)}")
    
    # Run optimized backtest
    print(f"\n{'='*80}")
    print("RUNNING OPTIMIZED BACKTEST")
    print(f"{'='*80}")
    
    all_results = []
    for symbol in filtered_symbols:
        result = optimized.backtest_stock_optimized(symbol, start_date, end_date, sector_map)
        if result:
            all_results.append(result)
    
    if all_results:
        # Summary
        print(f"\n{'='*80}")
        print("OPTIMIZED STRATEGY RESULTS")
        print(f"{'='*80}\n")
        
        summary_df = pd.DataFrame([{
            'Symbol': r['symbol'],
            'Trades': r['total_trades'],
            'Win Rate': f"{r['win_rate']:.1f}%",
            'Avg Profit': f"{r['avg_profit_pct']:+.2f}%",
            'Total Return': f"{r['total_return_pct']:+.2f}%"
        } for r in all_results])
        
        print(summary_df.to_string(index=False))
        
        # Overall stats
        total_trades = sum(r['total_trades'] for r in all_results)
        total_winning = sum(r['winning_trades'] for r in all_results)
        overall_win_rate = (total_winning / total_trades * 100) if total_trades > 0 else 0
        avg_return = sum(r['total_return_pct'] for r in all_results) / len(all_results)
        
        print(f"\n{'='*80}")
        print("OVERALL PERFORMANCE")
        print(f"{'='*80}")
        print(f"Stocks Traded:     {len(all_results)}")
        print(f"Total Trades:      {total_trades}")
        print(f"Overall Win Rate:  {overall_win_rate:.1f}%")
        print(f"Avg Return/Stock:  {avg_return:+.2f}%")
        
        print(f"\n{'='*80}")
        print("KEY IMPROVEMENTS")
        print(f"{'='*80}")
        print("✓ Sector rotation: Only trading strong sectors")
        print("✓ Stock selection: Only top performers")
        print("✓ Market timing: Only when NIFTY bullish")
        print("✓ Trailing stops: Protecting profits")
        print("✓ Dynamic sizing: Larger bets on strong signals")
        print("✓ Stricter entry: Higher quality trades")


if __name__ == "__main__":
    run_comparison()

# Made with Bob
