"""
Advanced Portfolio Analysis with Date-Stamped CSV and HTML Output
BUY signals based on:
- Relative Strength vs NIFTY
- Volume Expansion
- Sector Strength

Outputs:
- CSV file with date stamp (once per day)
- HTML visualization report (once per day)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators
from file_manager import DateStampedFileManager
import pandas as pd
import time
from datetime import datetime
import json

# Portfolio with sector classification
PORTFOLIO = {
    # Banking
    'HDFCBANK': 'Banking',
    'ICICIBANK': 'Banking',
    'SBIN': 'Banking',

    # Information Technology
    'INFY': 'IT',
    'TCS': 'IT',

    # Energy / Oil & Gas
    'RELIANCE': 'Energy',
    'IOC': 'Energy',
    'OIL': 'Energy',

    # FMCG / Consumer Goods
    'ITC': 'FMCG',
    'HINDUNILVR': 'FMCG',
    'ASIANPAINT': 'FMCG',

    # Infrastructure / Engineering / Capital Goods
    'LT': 'Infrastructure',

    # Metals & Mining
    'VEDL': 'Metals & Mining',
    'SAIL': 'Metals & Mining',
    'TATASTEEL': 'Metals & Mining',

    # Power / Utilities
    'PFC': 'Power Finance',
    'ADANIPOWER': 'Power & Utilities',

    # Railway / Transportation
    'IRCTC': 'Railways & Tourism',

    # Conglomerates / Diversified
    'ADANIENT': 'Diversified',

    # Financial Services / NBFC / Fintech
    'JIOFIN': 'Financial Services',

    'HAL': 'Aerospace & Defence',
    'GAIL': 'Energy',

    'TMPV': 'Automobile',
    'TMCV': 'Automobile',
    'MOTILALOFS': 'Financial Services',

}


def analyze_portfolio(force_regenerate=False):
    """
    Main portfolio analysis function
    
    Args:
        force_regenerate: If True, regenerate files even if they exist for today
    """
    print("="*90)
    print("ADVANCED PORTFOLIO ANALYSIS WITH OUTPUT")
    print("Signals based on: Relative Strength | Volume Expansion | Sector Strength")
    print("="*90)
    
    # Initialize file manager
    file_manager = DateStampedFileManager(output_dir='output')
    
    # Note: We now append to CSV, so we don't skip based on file existence
    csv_file = file_manager.get_csv_filename('portfolio_analysis')
    html_file = file_manager.get_html_filename('portfolio_analysis')
    
    fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')
    
    # Step 1: Fetch NIFTY data for relative strength
    print("\n📊 Fetching NIFTY 50 index data...")
    
    nifty_symbols = ['^NSEI', 'NIFTY', '^NSEBANK', 'NSEI.NS']
    nifty_data = None
    
    for nifty_symbol in nifty_symbols:
        try:
            print(f"   Trying {nifty_symbol}...", end=" ")
            if nifty_symbol.startswith('^'):
                data = fetcher.fetch_stock_data(nifty_symbol, exchange='', days=60)
            else:
                data = fetcher.fetch_stock_data(nifty_symbol, exchange='NSE', days=60)
            
            if data is not None and not data.empty and len(data) > 10:
                nifty_data = data
                print(f"✓ Success!")
                break
            else:
                print("✗ No data")
        except:
            print("✗ Failed")
    
    if nifty_data is None or nifty_data.empty:
        print("\n⚠️  Could not fetch NIFTY data from any source.")
        print("   Relative Strength analysis will be disabled.")
        nifty_data = None
    else:
        nifty_data = MomentumIndicators.add_all_momentum_indicators(nifty_data)
        print(f"✓ NIFTY data fetched ({len(nifty_data)} days)")
    
    # Step 2: Analyze each stock
    print(f"\n📈 Analyzing {len(PORTFOLIO)} stocks...")
    results = []
    sector_data = {}
    
    for i, (symbol, sector) in enumerate(PORTFOLIO.items(), 1):
        print(f"\n[{i}/{len(PORTFOLIO)}] {symbol} ({sector})...", end=" ")
        
        try:
            data = fetcher.fetch_stock_data(symbol, exchange='NSE', days=60)
            
            if data is None or data.empty:
                print("❌ No data")
                continue
            
            data = MomentumIndicators.add_all_momentum_indicators(data)
            data = TrendIndicators.add_all_trend_indicators(data)
            
            # Calculate EMA 20 if not present
            if 'EMA_20' not in data.columns:
                # Calculate EMA manually
                data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
            
            latest = data.iloc[-1]
            prev_5 = data.iloc[-6] if len(data) > 5 else data.iloc[0]
            prev_20 = data.iloc[-21] if len(data) > 20 else data.iloc[0]
            
            # Calculate scores
            rs_score, rs_value = calculate_relative_strength(latest, prev_5, prev_20, nifty_data)
            volume_score, volume_ratio = calculate_volume_score(data, latest)
            momentum_score = calculate_momentum_score(latest)
            
            # Add EMA score to strategy
            ema_score = calculate_ema_score(latest, data.iloc[-1])
            
            total_score = rs_score + volume_score + momentum_score + ema_score
            signal, emoji = determine_signal(total_score)
            
            # Calculate EMA 20 and price vs EMA
            ema_20 = latest['EMA_20'] if pd.notna(latest['EMA_20']) else latest['Close']
            price_vs_ema = ((latest['Close'] - ema_20) / ema_20 * 100) if ema_20 > 0 else 0
            
            result = {
                'Symbol': symbol,
                'Sector': sector,
                'Close': latest['Close'],
                'EMA_20': ema_20,
                'Price_vs_EMA': price_vs_ema,
                'RSI': latest['RSI'],
                'Momentum': latest['Momentum_Score'],
                'RS_Score': rs_score,
                'RS_Value': rs_value,
                'Vol_Ratio': volume_ratio,
                'Vol_Score': volume_score,
                'Mom_Score': momentum_score,
                'EMA_Score': ema_score,
                'Total_Score': total_score,
                'Signal': signal,
                'Emoji': emoji,
                'Trend': 'Bullish' if latest['SuperTrend_Direction'] == 1 else 'Bearish',
                'Score_Trend': 'NEW',  # Will be updated later
                'Trend_Emoji': '🆕',   # Will be updated later
                'Date': file_manager.today
            }
            
            results.append(result)
            
            if sector not in sector_data:
                sector_data[sector] = []
            sector_data[sector].append(total_score)
            
            print(f"✓ Score: {total_score}")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ {str(e)[:40]}")
    
    if not results:
        print("\n❌ No data fetched.")
        return None, None
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Load previous data to calculate score trends
    csv_file_path = file_manager.get_csv_filename('portfolio_analysis')
    previous_scores = {}
    
    print(f"\n📊 Loading previous scores from: {csv_file_path}")
    
    if os.path.exists(csv_file_path):
        try:
            previous_df = pd.read_csv(csv_file_path)
            print(f"   Found {len(previous_df)} previous records")
            
            # Get the most recent entry for each symbol (before current run)
            if not previous_df.empty and 'Symbol' in previous_df.columns and 'Total_Score' in previous_df.columns:
                # If we have at least 20 records (one full run), use previous run's data
                if len(previous_df) >= 20:
                    # Get the second-to-last complete set of data
                    # Group by timestamp if available, otherwise use last 20 records
                    if 'Timestamp' in previous_df.columns:
                        # Get unique timestamps and use the second most recent
                        unique_timestamps = previous_df['Timestamp'].unique()
                        if len(unique_timestamps) >= 2:
                            # Use second most recent timestamp
                            prev_timestamp = sorted(unique_timestamps)[-2]
                            prev_data = previous_df[previous_df['Timestamp'] == prev_timestamp]
                            print(f"   Using data from previous run: {prev_timestamp}")
                        else:
                            # Only one timestamp, use it
                            prev_data = previous_df[previous_df['Timestamp'] == unique_timestamps[0]]
                            print(f"   Using data from first run: {unique_timestamps[0]}")
                    else:
                        # No timestamp column, use records before the last 20
                        prev_data = previous_df.iloc[:-20] if len(previous_df) > 20 else previous_df
                        print(f"   Using previous {len(prev_data)} records")
                    
                    if len(prev_data) > 0:
                        # Get the most recent score for each symbol from previous data
                        # Ensure prev_data is a DataFrame
                        if isinstance(prev_data, pd.DataFrame):
                            unique_symbols = prev_data['Symbol'].unique()
                            for symbol in unique_symbols:
                                symbol_mask = prev_data['Symbol'] == symbol
                                symbol_rows = prev_data[symbol_mask]
                                if len(symbol_rows) > 0:
                                    # Get the last entry for this symbol
                                    previous_scores[symbol] = symbol_rows.iloc[-1]['Total_Score']
                            
                            print(f"   Loaded previous scores for {len(previous_scores)} symbols")
                        else:
                            print(f"   Previous data is not a DataFrame")
                    else:
                        print(f"   No previous data available for comparison")
                else:
                    print(f"   Not enough data yet for trend comparison (need at least 20 records)")
            else:
                print(f"   CSV missing required columns")
        except Exception as e:
            print(f"   ⚠️  Could not load previous scores: {str(e)}")
    else:
        print(f"   No previous CSV file found (first run)")
    
    # Add trend indicators
    df['Score_Trend'] = df.apply(
        lambda row: calculate_score_trend(row['Symbol'], row['Total_Score'], previous_scores),
        axis=1
    )
    df['Trend_Emoji'] = df['Score_Trend'].apply(get_trend_emoji)
    
    df = df.sort_values('Total_Score', ascending=False)
    
    # Calculate sector strength
    sector_strength = {}
    for sector, scores in sector_data.items():
        sector_strength[sector] = sum(scores) / len(scores) if scores else 0
    
    # Display console output
    display_analysis_results(df, sector_strength, results)
    
    # Save to CSV (append mode)
    csv_file = file_manager.save_to_csv(df, 'portfolio_analysis', append=True)
    
    # Generate and save HTML (always regenerate to show latest data)
    html_content = generate_html_report(df, sector_strength, file_manager.today)
    html_file = file_manager.save_html(html_content, 'portfolio_analysis', force=True)
    
    print("\n" + "="*90)
    print("✅ ANALYSIS COMPLETE!")
    print("="*90)
    print(f"\n📄 CSV File: {csv_file}")
    print(f"🌐 HTML Report: {html_file}")
    print(f"\nOpen the HTML file in your browser to view the interactive dashboard.")
    
    return csv_file, html_file


def calculate_relative_strength(latest, prev_5, prev_20, nifty_data):
    """Calculate relative strength vs NIFTY - AGGRESSIVE 10%+ STRATEGY"""
    rs_score = 0
    rs_value = 0
    
    if nifty_data is not None and len(nifty_data) > 0:
        stock_return_5d = ((latest['Close'] - prev_5['Close']) / prev_5['Close'] * 100)
        stock_return_20d = ((latest['Close'] - prev_20['Close']) / prev_20['Close'] * 100)
        
        nifty_latest = nifty_data.iloc[-1]
        nifty_prev_5 = nifty_data.iloc[-6] if len(nifty_data) > 5 else nifty_data.iloc[0]
        nifty_prev_20 = nifty_data.iloc[-21] if len(nifty_data) > 20 else nifty_data.iloc[0]
        
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
    
    return rs_score, rs_value


def calculate_volume_score(data, latest):
    """Calculate volume expansion score - AGGRESSIVE 10%+ STRATEGY"""
    volume_score = 0
    volume_ratio = 0
    
    if 'Volume' in data.columns:
        avg_volume_20 = data['Volume'].tail(20).mean()
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
    
    return volume_score, volume_ratio


def calculate_momentum_score(latest):
    """Calculate momentum score - AGGRESSIVE 10%+ STRATEGY"""
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
    
    return momentum_score


def calculate_score_trend(symbol, current_score, previous_scores):
    """Calculate if score is rising, falling, or stable"""
    if symbol not in previous_scores:
        return "NEW"
    
    prev_score = previous_scores[symbol]
    diff = current_score - prev_score
    
    if diff > 5:
        return "RISING"
    elif diff < -5:
        return "FALLING"
    else:
        return "STABLE"


def get_trend_emoji(trend):
    """Get emoji for trend direction"""
    if trend == "RISING":
        return "📈"
    elif trend == "FALLING":
        return "📉"
    elif trend == "STABLE":
        return "➡️"
    else:  # NEW
        return "🆕"


def calculate_ema_score(latest, data_row):
    """Calculate EMA score - AGGRESSIVE 10%+ STRATEGY"""
    ema_score = 0
    price_vs_ema = 0
    
    if 'EMA_20' in data_row.index and pd.notna(data_row['EMA_20']):
        ema_20 = data_row['EMA_20']
        if ema_20 > 0:
            price_vs_ema = ((latest['Close'] - ema_20) / ema_20 * 100)
            
            # Very strong bullish: Price > 8% above EMA
            if price_vs_ema > 8:
                ema_score = 30
            # Strong bullish: Price 5-8% above EMA
            elif price_vs_ema > 5:
                ema_score = 25
            # Bullish: Price 3-5% above EMA
            elif price_vs_ema > 3:
                ema_score = 20
            # Mildly bullish: Price 1-3% above EMA
            elif price_vs_ema > 1:
                ema_score = 15
            # Neutral: Price 0-1% above EMA
            elif price_vs_ema > 0:
                ema_score = 5
            # Mildly bearish: Price 0-2% below EMA
            elif price_vs_ema > -2:
                ema_score = -10
            # Bearish: Price 2-5% below EMA
            elif price_vs_ema > -5:
                ema_score = -20
            # Strong bearish: Price > 5% below EMA
            else:
                ema_score = -30
    
    return ema_score


def determine_signal(total_score):
    """Determine buy/sell signal based on total score - AGGRESSIVE 10%+ STRATEGY"""
    if total_score >= 80:  # Only the absolute best setups
        return "STRONG BUY", "🟢"
    elif total_score >= 60:
        return "BUY", "🟢"
    elif total_score >= 0:
        return "HOLD", "🟡"
    elif total_score >= -40:
        return "SELL", "🔴"
    else:
        return "STRONG SELL", "🔴"


def display_analysis_results(df, sector_strength, results):
    """Display analysis results in console"""
    print("\n" + "="*90)
    print("DETAILED ANALYSIS")
    print("="*90)
    print()
    
    for _, row in df.iterrows():
        sector_avg = sector_strength.get(row['Sector'], 0)
        sector_status = "🔥" if sector_avg > 30 else "📈" if sector_avg > 0 else "📉"
        
        # EMA status
        ema_status = "🟢" if row['Price_vs_EMA'] > 0 else "🔴"
        
        # Score trend indicator
        trend_indicator = f"{row['Trend_Emoji']} {row['Score_Trend']}" if 'Trend_Emoji' in row.index else ""
        
        print(f"{row['Emoji']} {row['Symbol']:12} {row['Sector']:15} ₹{row['Close']:8.2f} {trend_indicator}")
        print(f"   RS: {row['RS_Value']:+6.2f}% ({row['RS_Score']:+3}) | "
              f"Vol: {row['Vol_Ratio']:4.2f}x ({row['Vol_Score']:+3}) | "
              f"Mom: {row['Mom_Score']:+3} | "
              f"EMA: {row['EMA_Score']:+3} | "
              f"Total: {row['Total_Score']:3} | "
              f"{row['Signal']}")
        print(f"   EMA(20): {ema_status} ₹{row['EMA_20']:.2f} ({row['Price_vs_EMA']:+.2f}%) | "
              f"Sector: {sector_status} {sector_avg:+.1f}")
        print()


def generate_html_report(df, sector_strength, date_str):
    """Generate HTML visualization report"""
    
    # Prepare data for charts
    symbols = df['Symbol'].tolist()
    total_scores = df['Total_Score'].tolist()
    rs_values = df['RS_Value'].tolist()
    vol_ratios = df['Vol_Ratio'].tolist()
    
    # Sector data
    sorted_sectors = sorted(sector_strength.items(), key=lambda x: x[1], reverse=True)
    sector_names = [s[0] for s in sorted_sectors]
    sector_scores = [s[1] for s in sorted_sectors]
    
    # Signal distribution
    signal_counts = df['Signal'].value_counts().to_dict()
    
    # Trend data for chart
    trend_counts = df['Score_Trend'].value_counts().to_dict()
    trend_labels = ['RISING', 'FALLING', 'STABLE', 'NEW']
    trend_values = [trend_counts.get(label, 0) for label in trend_labels]
    trend_colors = ['rgba(40, 167, 69, 0.6)', 'rgba(220, 53, 69, 0.6)', 'rgba(255, 193, 7, 0.6)', 'rgba(108, 117, 125, 0.6)']
    trend_border_colors = ['rgb(40, 167, 69)', 'rgb(220, 53, 69)', 'rgb(255, 193, 7)', 'rgb(108, 117, 125)']
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Analysis - {date_str}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-card h3 {{
            color: #2a5298;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .charts-section {{
            padding: 30px;
        }}
        
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            color: #2a5298;
            font-size: 1.6em;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
        }}
        
        .data-table {{
            padding: 30px;
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .signal-strong-buy {{ color: #28a745; font-weight: bold; }}
        .signal-buy {{ color: #5cb85c; font-weight: bold; }}
        .signal-hold {{ color: #ffc107; font-weight: bold; }}
        .signal-sell {{ color: #dc3545; font-weight: bold; }}
        .signal-strong-sell {{ color: #c82333; font-weight: bold; }}
        
        .footer {{
            background: #2a5298;
            color: white;
            text-align: center;
            padding: 25px;
            font-size: 0.95em;
        }}
        
        .emoji {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Portfolio Analysis Dashboard</h1>
            <p>Analysis Date: {date_str} | Total Stocks: {len(df)}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>🟢 Strong Buy / Buy</h3>
                <div class="stat-value">{signal_counts.get('STRONG BUY', 0) + signal_counts.get('BUY', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>🟡 Hold</h3>
                <div class="stat-value">{signal_counts.get('HOLD', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>🔴 Sell / Strong Sell</h3>
                <div class="stat-value">{signal_counts.get('SELL', 0) + signal_counts.get('STRONG SELL', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>📈 Avg Total Score</h3>
                <div class="stat-value">{df['Total_Score'].mean():.1f}</div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📈 Rising Momentum</h3>
                <div class="stat-value">{(df['Score_Trend'] == 'RISING').sum()}</div>
                <p style="margin-top: 10px; color: #28a745;">Stocks gaining strength</p>
            </div>
            <div class="stat-card">
                <h3>📉 Falling Momentum</h3>
                <div class="stat-value">{(df['Score_Trend'] == 'FALLING').sum()}</div>
                <p style="margin-top: 10px; color: #dc3545;">Stocks losing strength</p>
            </div>
            <div class="stat-card">
                <h3>➡️ Stable</h3>
                <div class="stat-value">{(df['Score_Trend'] == 'STABLE').sum()}</div>
                <p style="margin-top: 10px; color: #ffc107;">Maintaining position</p>
            </div>
            <div class="stat-card">
                <h3>🆕 New Entries</h3>
                <div class="stat-value">{(df['Score_Trend'] == 'NEW').sum()}</div>
                <p style="margin-top: 10px; color: #6c757d;">First time tracked</p>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <h2 class="chart-title">📊 Score Momentum Trends</h2>
                <p style="text-align: center; color: #666; margin-bottom: 20px;">
                    Track which stocks are gaining or losing momentum over time
                </p>
                <canvas id="trendChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">Stock Total Scores</h2>
                <canvas id="scoresChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">Sector Strength Analysis</h2>
                <canvas id="sectorChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">Relative Strength vs NIFTY</h2>
                <canvas id="rsChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">Volume Expansion Ratios</h2>
                <canvas id="volumeChart"></canvas>
            </div>
        </div>
        
        <div class="data-table">
            <h2 class="chart-title">Detailed Stock Analysis</h2>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Sector</th>
                        <th>Close (₹)</th>
                        <th>EMA(20)</th>
                        <th>vs EMA %</th>
                        <th>Signal</th>
                        <th>Total Score</th>
                        <th>Score Trend</th>
                        <th>RS Value (%)</th>
                        <th>Vol Ratio</th>
                        <th>RSI</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_table_rows(df)}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Advanced Portfolio Analyzer | Data for educational purposes only</p>
            <p>Analysis based on Relative Strength, Volume Expansion, and Sector Strength</p>
        </div>
    </div>
    
    <script>
        const chartConfig = {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{
                    display: true,
                    position: 'top'
                }}
            }}
        }};
        
        // Trend Chart (NEW)
        new Chart(document.getElementById('trendChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(trend_labels)},
                datasets: [{{
                    label: 'Score Trends',
                    data: {json.dumps(trend_values)},
                    backgroundColor: {json.dumps(trend_colors)},
                    borderColor: {json.dumps(trend_border_colors)},
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            font: {{
                                size: 14
                            }}
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                let label = context.label || '';
                                let value = context.parsed || 0;
                                let total = context.dataset.data.reduce((a, b) => a + b, 0);
                                let percentage = ((value / total) * 100).toFixed(1);
                                return label + ': ' + value + ' stocks (' + percentage + '%)';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Stock Scores Chart
        new Chart(document.getElementById('scoresChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(symbols)},
                datasets: [{{
                    label: 'Total Score',
                    data: {json.dumps(total_scores)},
                    backgroundColor: {json.dumps(['rgba(75, 192, 192, 0.6)' if s >= 40 else 'rgba(255, 206, 86, 0.6)' if s >= 0 else 'rgba(255, 99, 132, 0.6)' for s in total_scores])},
                    borderColor: {json.dumps(['rgb(75, 192, 192)' if s >= 40 else 'rgb(255, 206, 86)' if s >= 0 else 'rgb(255, 99, 132)' for s in total_scores])},
                    borderWidth: 2
                }}]
            }},
            options: {{
                ...chartConfig,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Sector Chart
        new Chart(document.getElementById('sectorChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(sector_names)},
                datasets: [{{
                    label: 'Sector Strength',
                    data: {json.dumps(sector_scores)},
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgb(102, 126, 234)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Relative Strength Chart
        new Chart(document.getElementById('rsChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(symbols)},
                datasets: [{{
                    label: 'RS Value (%)',
                    data: {json.dumps(rs_values)},
                    backgroundColor: {json.dumps(['rgba(75, 192, 192, 0.6)' if r > 0 else 'rgba(255, 99, 132, 0.6)' for r in rs_values])},
                    borderColor: {json.dumps(['rgb(75, 192, 192)' if r > 0 else 'rgb(255, 99, 132)' for r in rs_values])},
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Volume Chart
        new Chart(document.getElementById('volumeChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(symbols)},
                datasets: [{{
                    label: 'Volume Ratio',
                    data: {json.dumps(vol_ratios)},
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                    borderColor: 'rgb(153, 102, 255)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    return html_content


def generate_table_rows(df):
    """Generate HTML table rows from dataframe"""
    rows = ""
    for _, row in df.iterrows():
        signal_class = f"signal-{row['Signal'].lower().replace(' ', '-')}"
        ema_class = "buy" if row['Price_vs_EMA'] > 0 else "sell"
        
        # Get trend emoji and text
        trend_emoji = row.get('Trend_Emoji', '🆕')
        score_trend = row.get('Score_Trend', 'NEW')
        
        rows += f"""
            <tr>
                <td><span class="emoji">{row['Emoji']}</span> {row['Symbol']}</td>
                <td>{row['Sector']}</td>
                <td>₹{row['Close']:.2f}</td>
                <td>₹{row['EMA_20']:.2f}</td>
                <td class="{ema_class}">{row['Price_vs_EMA']:+.2f}%</td>
                <td class="{signal_class}">{row['Signal']}</td>
                <td>{row['Total_Score']}</td>
                <td><span class="emoji">{trend_emoji}</span> {score_trend}</td>
                <td>{row['RS_Value']:+.2f}%</td>
                <td>{row['Vol_Ratio']:.2f}x</td>
                <td>{row['RSI']:.1f}</td>
                <td>{row['Trend']}</td>
            </tr>
        """
    return rows


if __name__ == "__main__":
    # Run analysis
    # Set force_regenerate=True to regenerate files even if they exist for today
    csv_file, html_file = analyze_portfolio(force_regenerate=False)
    
    if csv_file and html_file:
        print("\n" + "="*90)
        print("🎉 SUCCESS! Files generated:")
        print(f"  📄 {csv_file}")
        print(f"  🌐 {html_file}")
        print("="*90)


# Made with Bob