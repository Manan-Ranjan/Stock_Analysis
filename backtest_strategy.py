"""
Backtesting System for Portfolio Analysis Strategy
Tests the effectiveness of BUY/SELL signals based on historical data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators
from file_manager import DateStampedFileManager
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class StrategyBacktester:
    """Backtest portfolio analysis strategy"""
    
    def __init__(self, initial_capital=100000, position_size=0.1):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital in INR
            position_size: Fraction of capital to allocate per position (0.1 = 10%)
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')
        
    def calculate_signal_score(self, data, nifty_data, index):
        """
        Calculate signal score for a specific date
        
        Args:
            data: Stock price data
            nifty_data: NIFTY index data
            index: Index position in the dataframe
            
        Returns:
            tuple: (total_score, signal, details_dict)
        """
        if index < 20:  # Need at least 20 days of history
            return 0, "HOLD", {}
        
        latest = data.iloc[index]
        prev_5 = data.iloc[index-5] if index >= 5 else data.iloc[0]
        prev_20 = data.iloc[index-20] if index >= 20 else data.iloc[0]
        
        # Relative Strength
        rs_score = 0
        rs_value = 0
        
        if nifty_data is not None and len(nifty_data) > index:
            stock_return_5d = ((latest['Close'] - prev_5['Close']) / prev_5['Close'] * 100)
            stock_return_20d = ((latest['Close'] - prev_20['Close']) / prev_20['Close'] * 100)
            
            nifty_latest = nifty_data.iloc[index]
            nifty_prev_5 = nifty_data.iloc[index-5] if index >= 5 else nifty_data.iloc[0]
            nifty_prev_20 = nifty_data.iloc[index-20] if index >= 20 else nifty_data.iloc[0]
            
            nifty_return_5d = ((nifty_latest['Close'] - nifty_prev_5['Close']) / nifty_prev_5['Close'] * 100)
            nifty_return_20d = ((nifty_latest['Close'] - nifty_prev_20['Close']) / nifty_prev_20['Close'] * 100)
            
            rs_5d = stock_return_5d - nifty_return_5d
            rs_20d = stock_return_20d - nifty_return_20d
            rs_value = (rs_5d + rs_20d) / 2
            
            # STRICTER RS requirements - must outperform significantly
            if rs_value > 8:  # Increased from 5
                rs_score = 35  # Increased reward
            elif rs_value > 5:  # Increased from 2
                rs_score = 25
            elif rs_value > 2:  # Increased from 0
                rs_score = 15
            elif rs_value > 0:
                rs_score = 5
            elif rs_value > -2:
                rs_score = -15  # Increased penalty
            else:
                rs_score = -25  # Increased penalty
        
        # Volume Score
        volume_score = 0
        volume_ratio = 0
        
        if 'Volume' in data.columns and index >= 20:
            avg_volume_20 = data['Volume'].iloc[index-20:index].mean()
            current_volume = latest['Volume']
            volume_ratio = (current_volume / avg_volume_20) if avg_volume_20 > 0 else 1
            
            # STRICTER volume requirements - need strong volume confirmation
            if volume_ratio > 2.5:  # Increased from 2.0
                volume_score = 30  # Increased reward
            elif volume_ratio > 2.0:  # Increased from 1.5
                volume_score = 25
            elif volume_ratio > 1.5:  # Increased from 1.2
                volume_score = 20
            elif volume_ratio > 1.2:
                volume_score = 10
            elif volume_ratio > 0.8:
                volume_score = 0  # Neutral instead of positive
            else:
                volume_score = -15  # Increased penalty
        
        # Momentum Score - ENHANCED for 10%+ profit
        momentum_score = 0
        
        # RSI scoring - reward strong momentum
        if latest['RSI'] > 65:
            momentum_score += 20  # Increased from 15
        elif latest['RSI'] > 55:
            momentum_score += 15  # Increased from 10
        elif latest['RSI'] > 50:
            momentum_score += 10
        elif latest['RSI'] < 40:
            momentum_score -= 15  # Increased penalty
        elif latest['RSI'] < 30:
            momentum_score -= 25  # Strong penalty for oversold
        
        # SuperTrend - critical indicator
        if latest['SuperTrend_Direction'] == 1:
            momentum_score += 20  # Increased from 15
        else:
            momentum_score -= 20  # Increased penalty
        
        # SMA confirmation
        if latest['Close'] > latest['SMA_20']:
            momentum_score += 15  # Increased from 10
        else:
            momentum_score -= 10  # Add penalty for below SMA
        
        # EMA Score - CRITICAL for 10%+ profit strategy
        ema_score = 0
        price_vs_ema = 0
        if 'EMA_20' not in data.columns:
            data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
        
        ema_20 = data['EMA_20'].iloc[index]
        if pd.notna(ema_20) and ema_20 > 0:
            price_vs_ema = ((latest['Close'] - ema_20) / ema_20 * 100)
            
            # Very strong bullish: Price > 8% above EMA
            if price_vs_ema > 8:
                ema_score = 30  # Increased from 20
            # Strong bullish: Price 5-8% above EMA
            elif price_vs_ema > 5:
                ema_score = 25  # Increased from 20
            # Bullish: Price 3-5% above EMA
            elif price_vs_ema > 3:
                ema_score = 20  # Increased from 15
            # Mildly bullish: Price 1-3% above EMA
            elif price_vs_ema > 1:
                ema_score = 15  # Increased from 10
            # Neutral: Price 0-1% above EMA
            elif price_vs_ema > 0:
                ema_score = 5
            # Mildly bearish: Price 0-2% below EMA
            elif price_vs_ema > -2:
                ema_score = -10  # Increased penalty
            # Bearish: Price 2-5% below EMA
            elif price_vs_ema > -5:
                ema_score = -20  # Increased penalty
            # Strong bearish: Price > 5% below EMA
            else:
                ema_score = -30  # Increased penalty
        
        # Total Score (now includes EMA)
        total_score = rs_score + volume_score + momentum_score + ema_score
        
        # Determine Signal - VERY STRICT for 10%+ profit target
        if total_score >= 80:  # Only the absolute best setups
            signal = "STRONG BUY"
        elif total_score >= 60:
            signal = "BUY"
        elif total_score >= 0:
            signal = "HOLD"
        elif total_score >= -40:
            signal = "SELL"
        else:
            signal = "STRONG SELL"
        
        details = {
            'rs_score': rs_score,
            'rs_value': rs_value,
            'volume_score': volume_score,
            'volume_ratio': volume_ratio,
            'momentum_score': momentum_score,
            'ema_score': ema_score,
            'price_vs_ema': price_vs_ema,
            'rsi': latest['RSI'],
            'close': latest['Close']
        }
        
        return total_score, signal, details
    
    def backtest_stock(self, symbol, start_date, end_date, holding_days=5):
        """
        Backtest strategy for a single stock
        
        Args:
            symbol: Stock symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            holding_days: Number of days to hold position after BUY signal
            
        Returns:
            dict: Backtest results
        """
        print(f"\n{'='*60}")
        print(f"Backtesting {symbol}")
        print(f"{'='*60}")
        
        # Fetch data
        days_needed = (end_date - start_date).days + 60  # Extra for indicators
        data = self.fetcher.fetch_stock_data(symbol, exchange='NSE', days=days_needed)
        
        if data is None or data.empty:
            print(f"❌ No data for {symbol}")
            return None
        
        # Add indicators
        data = MomentumIndicators.add_all_momentum_indicators(data)
        data = TrendIndicators.add_all_trend_indicators(data)
        
        # Fetch NIFTY data
        nifty_data = None
        for nifty_symbol in ['^NSEI', 'NIFTY']:
            try:
                nifty_data = self.fetcher.fetch_stock_data(nifty_symbol, exchange='', days=days_needed)
                if nifty_data is not None and not nifty_data.empty:
                    nifty_data = MomentumIndicators.add_all_momentum_indicators(nifty_data)
                    break
            except:
                continue
        
        # Simulate trading
        trades = []
        position = None
        capital = self.initial_capital
        
        # Reset index to ensure we have proper datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            data = data.reset_index()
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date'])
                data = data.set_index('Date')
            elif 'index' in data.columns:
                data['index'] = pd.to_datetime(data['index'])
                data = data.set_index('index')
        
        for i in range(20, len(data)):
            current_date = data.index[i]
            if not isinstance(current_date, pd.Timestamp):
                current_date = pd.to_datetime(current_date)
            
            # Skip if outside backtest period
            if current_date < start_date or current_date > end_date:
                continue
            
            # Calculate signal
            score, signal, details = self.calculate_signal_score(data, nifty_data, i)
            current_price = details['close']
            
            # Check if we have an open position
            if position is not None:
                days_held = (current_date - position['entry_date']).days
                
                # Exit conditions - AGGRESSIVE for 10%+ profit target
                should_exit = False
                exit_reason = ""
                
                # Calculate current profit/loss
                current_pnl_pct = ((current_price - position['entry_price']) / position['entry_price']) * 100
                
                # 1. Very tight stop loss (3% instead of 5%)
                if current_price <= position['entry_price'] * 0.97:
                    should_exit = True
                    exit_reason = "Stop loss (3%)"
                
                # 2. Aggressive trailing stop - Lock in profits after 6% gain
                elif current_pnl_pct >= 6:
                    # If price drops 2% from peak, exit
                    if 'peak_price' not in position:
                        position['peak_price'] = current_price
                    else:
                        position['peak_price'] = max(position['peak_price'], current_price)
                    
                    trailing_stop_price = position['peak_price'] * 0.98
                    if current_price <= trailing_stop_price:
                        should_exit = True
                        exit_reason = f"Trailing stop (locked profit: {current_pnl_pct:.1f}%)"
                
                # 3. Primary target: 12% profit (aim higher than 10%)
                elif current_price >= position['entry_price'] * 1.12:
                    should_exit = True
                    exit_reason = "Take profit (12%)"
                
                # 4. Exit on any signal deterioration
                elif signal in ["SELL", "STRONG SELL", "HOLD", "BUY"]:
                    # Only stay in STRONG BUY, exit everything else
                    if signal != "STRONG BUY":
                        should_exit = True
                        exit_reason = f"Signal weakened: {signal}"
                
                # 5. Shorter holding period (3 days instead of 5)
                elif days_held >= 3:
                    should_exit = True
                    exit_reason = f"Holding period (3 days)"
                
                if should_exit:
                    # Close position
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
            
            # Check for new BUY signal - ULTRA STRICT for 10%+ profit
            elif signal == "STRONG BUY" and position is None:
                # Additional filters before entry - VERY STRICT
                entry_allowed = True
                
                # Filter 1: RSI must be in sweet spot (50-70)
                if details['rsi'] < 50 or details['rsi'] > 70:
                    entry_allowed = False
                
                # Filter 2: Price must be significantly above EMA (> 2%)
                if details['price_vs_ema'] < 2:
                    entry_allowed = False
                
                # Filter 3: Strong volume required (> 1.5x average)
                if details['volume_ratio'] < 1.5:
                    entry_allowed = False
                
                # Filter 4: Must have strong relative strength (> 5%)
                if details['rs_value'] < 5:
                    entry_allowed = False
                
                # Filter 5: SuperTrend must be bullish
                if data.iloc[i]['SuperTrend_Direction'] != 1:
                    entry_allowed = False
                
                if entry_allowed:
                    # Enter position
                    position_value = capital * self.position_size
                    shares = int(position_value / current_price)
                else:
                    continue
                
                if shares > 0:
                    entry_value = shares * current_price
                    
                    position = {
                        'entry_date': current_date,
                        'entry_price': current_price,
                        'entry_signal': signal,
                        'entry_score': score,
                        'shares': shares,
                        'entry_value': entry_value
                    }
                    
                    capital -= entry_value
                    
                    date_str = pd.to_datetime(current_date).strftime('%Y-%m-%d')
                    print(f"  {'ENTRY':<6} {date_str} | "
                          f"₹{current_price:8.2f} | {signal:<12} | "
                          f"Score: {score:3d} | Shares: {shares}")
        
        # Close any open position at end
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
        
        # Calculate statistics
        if not trades:
            print(f"\n⚠️  No trades executed for {symbol}")
            return None
        
        trades_df = pd.DataFrame(trades)
        
        total_return = capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        winning_trades = trades_df[trades_df['profit'] > 0]
        losing_trades = trades_df[trades_df['profit'] < 0]
        
        win_rate = (len(winning_trades) / len(trades_df)) * 100 if len(trades_df) > 0 else 0
        avg_profit = trades_df['profit'].mean()
        avg_profit_pct = trades_df['profit_pct'].mean()
        
        max_profit = trades_df['profit'].max()
        max_loss = trades_df['profit'].min()
        
        results = {
            'symbol': symbol,
            'total_trades': len(trades_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'avg_profit': avg_profit,
            'avg_profit_pct': avg_profit_pct,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'final_capital': capital,
            'trades': trades_df
        }
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"BACKTEST RESULTS - {symbol}")
        print(f"{'='*60}")
        print(f"Total Trades:      {len(trades_df)}")
        print(f"Winning Trades:    {len(winning_trades)} ({win_rate:.1f}%)")
        print(f"Losing Trades:     {len(losing_trades)}")
        print(f"Avg Profit/Trade:  ₹{avg_profit:,.2f} ({avg_profit_pct:+.2f}%)")
        print(f"Max Profit:        ₹{max_profit:,.2f}")
        print(f"Max Loss:          ₹{max_loss:,.2f}")
        print(f"Total Return:      ₹{total_return:,.2f} ({total_return_pct:+.2f}%)")
        print(f"Final Capital:     ₹{capital:,.2f}")
        
        return results
    
    def backtest_portfolio(self, symbols, start_date, end_date, holding_days=5):
        """
        Backtest strategy across multiple stocks
        
        Args:
            symbols: List of stock symbols
            start_date: Start date for backtest
            end_date: End date for backtest
            holding_days: Number of days to hold position
            
        Returns:
            dict: Portfolio backtest results
        """
        print(f"\n{'='*80}")
        print(f"PORTFOLIO BACKTEST")
        print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Initial Capital: ₹{self.initial_capital:,.2f}")
        print(f"Position Size: {self.position_size*100:.0f}% per trade")
        print(f"Holding Period: {holding_days} days")
        print(f"{'='*80}")
        
        all_results = []
        
        for symbol in symbols:
            result = self.backtest_stock(symbol, start_date, end_date, holding_days)
            if result:
                all_results.append(result)
        
        if not all_results:
            print("\n❌ No successful backtests")
            return None
        
        # Portfolio summary
        print(f"\n{'='*80}")
        print(f"PORTFOLIO SUMMARY")
        print(f"{'='*80}")
        
        results_df = pd.DataFrame([{
            'Symbol': r['symbol'],
            'Trades': r['total_trades'],
            'Win Rate': f"{r['win_rate']:.1f}%",
            'Avg Profit': f"₹{r['avg_profit']:,.0f}",
            'Total Return': f"₹{r['total_return']:,.0f}",
            'Return %': f"{r['total_return_pct']:+.2f}%"
        } for r in all_results])
        
        print(results_df.to_string(index=False))
        
        # Overall statistics
        total_trades = sum(r['total_trades'] for r in all_results)
        total_winning = sum(r['winning_trades'] for r in all_results)
        overall_win_rate = (total_winning / total_trades * 100) if total_trades > 0 else 0
        
        avg_return_pct = np.mean([r['total_return_pct'] for r in all_results])
        best_stock = max(all_results, key=lambda x: x['total_return_pct'])
        worst_stock = min(all_results, key=lambda x: x['total_return_pct'])
        
        print(f"\n{'='*80}")
        print(f"OVERALL STATISTICS")
        print(f"{'='*80}")
        print(f"Stocks Tested:     {len(all_results)}")
        print(f"Total Trades:      {total_trades}")
        print(f"Overall Win Rate:  {overall_win_rate:.1f}%")
        print(f"Avg Return/Stock:  {avg_return_pct:+.2f}%")
        print(f"Best Performer:    {best_stock['symbol']} ({best_stock['total_return_pct']:+.2f}%)")
        print(f"Worst Performer:   {worst_stock['symbol']} ({worst_stock['total_return_pct']:+.2f}%)")
        
        return {
            'results': all_results,
            'summary': results_df,
            'total_trades': total_trades,
            'overall_win_rate': overall_win_rate,
            'avg_return_pct': avg_return_pct
        }


def run_backtest_example():
    """Example backtest run"""
    
    # Test stocks
    symbols = ['HDFCBANK', 'ICICIBANK', 'INFY', 'TCS', 'RELIANCE', 
               'ITC', 'ASIANPAINT', 'TATASTEEL', 'SAIL']
    
    # Backtest period (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Initialize backtester
    backtester = StrategyBacktester(
        initial_capital=100000,  # ₹1 lakh per stock
        position_size=0.9  # Use 90% of capital per trade
    )
    
    # Run backtest
    results = backtester.backtest_portfolio(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        holding_days=5  # Hold for 5 days
    )
    
    # Save results
    if results:
        file_manager = DateStampedFileManager(output_dir='backtest_results')
        
        # Save summary CSV
        csv_file = file_manager.get_csv_filename('backtest_summary')
        results['summary'].to_csv(csv_file, index=False)
        print(f"\n✓ Results saved to: {csv_file}")


if __name__ == "__main__":
    run_backtest_example()


# Made with Bob