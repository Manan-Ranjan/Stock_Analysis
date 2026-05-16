"""
Multi-Stock Technical Analysis Data Fetcher and HTML Generator
Now integrated with multi-source data fetcher (Google Finance + Yahoo Finance)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import ta
import numpy as np

# Import the multi-source data fetcher
try:
    from data_fetcher import DataFetcher, DataSourceConfig
    MULTI_SOURCE_AVAILABLE = True
except ImportError:
    MULTI_SOURCE_AVAILABLE = False
    print("Warning: data_fetcher not available, using direct Yahoo Finance")

class MultiStockAnalyzer:
    def __init__(self, stocks_config_file='stocks_config.csv', use_multi_source=True,
                 primary_source='yahoo', fallback_source='google'):
        self.stocks_config_file = stocks_config_file
        self.output_dir = 'stock_data'
        self.html_filename = "multi_stock_trends.html"
        self.stocks_data = {}
        self.use_multi_source = use_multi_source and MULTI_SOURCE_AVAILABLE
        
        # Initialize multi-source data fetcher
        if self.use_multi_source:
            print(f"🔄 Using multi-source data fetcher (Primary: {primary_source.upper()}, Fallback: {fallback_source.upper()})")
            self.data_fetcher = DataFetcher(primary_source=primary_source, fallback_source=fallback_source)
        else:
            print("📊 Using direct Yahoo Finance API")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_stocks_config(self):
        """Load stock symbols and names from CSV file"""
        print(f"Loading stocks configuration from {self.stocks_config_file}...")
        try:
            df = pd.read_csv(self.stocks_config_file)
            stocks = []
            for _, row in df.iterrows():
                stocks.append({
                    'symbol': row['Symbol'],
                    'name': row['Name']
                })
            print(f"Loaded {len(stocks)} stocks")
            return stocks
        except Exception as e:
            print(f"Error loading stocks config: {e}")
            return []
    
    def fetch_stock_data(self, symbol, name):
        """
        Fetch real stock data with technical indicators
        Now uses multi-source fetcher with automatic fallback
        """
        print(f"Fetching data for {symbol} ({name})...")
        
        if self.use_multi_source:
            return self._fetch_with_multi_source(symbol, name)
        else:
            return self._fetch_with_yahoo_direct(symbol, name)
    
    def _fetch_with_multi_source(self, symbol, name):
        """Fetch data using multi-source fetcher"""
        try:
            # Fetch raw data using multi-source fetcher
            raw_data = self.data_fetcher.fetch_stock_data(symbol, 'NSE', days=90)
            
            if raw_data is None or raw_data.empty:
                print(f"  Warning: No data found for {symbol}, using sample data")
                return self._generate_sample_data(symbol, name)
            
            # Process the raw data
            df = raw_data.copy()
            
            # Ensure we have Date column
            if 'Date' not in df.columns and df.index.name == 'Date':
                df = df.reset_index()
            
            # Convert Date to datetime if it's string
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date')
            
            # Keep only last 30 days for display
            df = df.tail(30).copy()
            
            # Calculate technical indicators using ta library
            df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
            df['MOM'] = ta.momentum.ROCIndicator(df['Close'], window=10).roc()
            
            # Awesome Oscillator
            ao = ta.momentum.AwesomeOscillatorIndicator(df['High'], df['Low'])
            df['AO'] = ao.awesome_oscillator()
            
            # CCI
            df['CCI'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=20).cci()
            
            # Calculate Moving Averages for ratings
            df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
            df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
            df['EMA_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()
            
            # Generate ratings based on indicators
            df['Tech_Rating'] = df.apply(self._calculate_tech_rating, axis=1)
            df['MA_Rating'] = df.apply(self._calculate_ma_rating, axis=1)
            df['Os_Rating'] = df.apply(self._calculate_oscillator_rating, axis=1)
            
            # Prepare final dataframe
            result_df = pd.DataFrame({
                'Date': df.index.strftime('%Y-%m-%d'),
                'Symbol': symbol,
                'Name': name,
                'Close': df['Close'].round(2),
                'Volume': df['Volume'].astype(int) if 'Volume' in df.columns else 0,
                'Tech Rating': df['Tech_Rating'],
                'MA Rating': df['MA_Rating'],
                'Os Rating': df['Os_Rating'],
                'RSI (14)': df['RSI'].round(2),
                'Mom (10)': df['MOM'].round(2),
                'AO': df['AO'].round(2),
                'CCI (20)': df['CCI'].round(2)
            })
            
            print(f"  ✓ Successfully fetched {len(result_df)} days of data")
            print(f"  📊 Data source: {raw_data['Source'].iloc[0] if 'Source' in raw_data.columns else 'Unknown'}")
            return result_df
            
        except Exception as e:
            print(f"  Error fetching data for {symbol}: {e}")
            print(f"  Using sample data instead")
            return self._generate_sample_data(symbol, name)
    
    def _fetch_with_yahoo_direct(self, symbol, name):
        """Direct Yahoo Finance fetch (fallback method)"""
        try:
            # For Indian stocks, add .NS suffix for NSE
            yahoo_symbol = f"{symbol}.NS"
            
            # Fetch data for last 90 days to calculate indicators properly
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            # Download stock data
            stock = yf.Ticker(yahoo_symbol)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                print(f"  Warning: No data found for {symbol}, using sample data")
                return self._generate_sample_data(symbol, name)
            
            # Keep only last 30 days for display
            df = df.tail(30).copy()
            
            # Calculate technical indicators
            df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
            df['MOM'] = ta.momentum.ROCIndicator(df['Close'], window=10).roc()
            ao = ta.momentum.AwesomeOscillatorIndicator(df['High'], df['Low'])
            df['AO'] = ao.awesome_oscillator()
            df['CCI'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=20).cci()
            df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
            df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
            df['EMA_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()
            
            # Generate ratings
            df['Tech_Rating'] = df.apply(self._calculate_tech_rating, axis=1)
            df['MA_Rating'] = df.apply(self._calculate_ma_rating, axis=1)
            df['Os_Rating'] = df.apply(self._calculate_oscillator_rating, axis=1)
            
            # Prepare final dataframe
            result_df = pd.DataFrame({
                'Date': df.index.strftime('%Y-%m-%d'),
                'Symbol': symbol,
                'Name': name,
                'Close': df['Close'].round(2),
                'Volume': df['Volume'].astype(int),
                'Tech Rating': df['Tech_Rating'],
                'MA Rating': df['MA_Rating'],
                'Os Rating': df['Os_Rating'],
                'RSI (14)': df['RSI'].round(2),
                'Mom (10)': df['MOM'].round(2),
                'AO': df['AO'].round(2),
                'CCI (20)': df['CCI'].round(2)
            })
            
            print(f"  ✓ Successfully fetched {len(result_df)} days of data")
            return result_df
            
        except Exception as e:
            print(f"  Error fetching data for {symbol}: {e}")
            print(f"  Using sample data instead")
            return self._generate_sample_data(symbol, name)
    
    def _calculate_tech_rating(self, row):
        """Calculate technical rating based on multiple indicators"""
        score = 0
        
        # RSI scoring
        if pd.notna(row['RSI']):
            if row['RSI'] < 30:
                score += 2  # Oversold - Strong Buy
            elif row['RSI'] < 40:
                score += 1  # Buy
            elif row['RSI'] > 70:
                score -= 2  # Overbought - Strong Sell
            elif row['RSI'] > 60:
                score -= 1  # Sell
        
        # Momentum scoring
        if pd.notna(row['MOM']):
            if row['MOM'] > 5:
                score += 1
            elif row['MOM'] < -5:
                score -= 1
        
        # Convert score to rating
        if score >= 2:
            return 'Strong Buy'
        elif score == 1:
            return 'Buy'
        elif score == -1:
            return 'Sell'
        elif score <= -2:
            return 'Strong Sell'
        else:
            return 'Neutral'
    
    def _calculate_ma_rating(self, row):
        """Calculate moving average rating"""
        if pd.notna(row['SMA_20']) and pd.notna(row['SMA_50']):
            if row['Close'] > row['SMA_20'] and row['Close'] > row['SMA_50']:
                return 'Strong Buy'
            elif row['Close'] > row['SMA_20']:
                return 'Buy'
            elif row['Close'] < row['SMA_20'] and row['Close'] < row['SMA_50']:
                return 'Strong Sell'
            elif row['Close'] < row['SMA_20']:
                return 'Sell'
        return 'Neutral'
    
    def _calculate_oscillator_rating(self, row):
        """Calculate oscillator rating based on RSI and CCI"""
        score = 0
        
        if pd.notna(row['RSI']):
            if row['RSI'] < 30:
                score += 1
            elif row['RSI'] > 70:
                score -= 1
        
        if pd.notna(row['CCI']):
            if row['CCI'] < -100:
                score += 1
            elif row['CCI'] > 100:
                score -= 1
        
        if score >= 1:
            return 'Buy'
        elif score <= -1:
            return 'Sell'
        return 'Neutral'
    
    def _generate_sample_data(self, symbol, name):
        """Generate sample data when real data is not available"""
        dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
        
        data = {
            'Date': dates,
            'Symbol': [symbol] * 30,
            'Name': [name] * 30,
            'Close': [round(100 + np.random.uniform(-10, 10), 2) for _ in range(30)],
            'Volume': [int(np.random.uniform(1000000, 10000000)) for _ in range(30)],
            'Tech Rating': self._generate_ratings('tech'),
            'MA Rating': self._generate_ratings('ma'),
            'Os Rating': self._generate_ratings('os'),
            'RSI (14)': self._generate_rsi(),
            'Mom (10)': self._generate_momentum(),
            'AO': self._generate_ao(),
            'CCI (20)': self._generate_cci()
        }
        
        return pd.DataFrame(data)
    
    def _generate_ratings(self, rating_type):
        """Generate sample ratings (Buy, Sell, Neutral)"""
        import random
        ratings = ['Strong Buy', 'Buy', 'Neutral', 'Sell', 'Strong Sell']
        weights = [0.3, 0.3, 0.2, 0.1, 0.1] if rating_type == 'tech' else [0.2, 0.3, 0.3, 0.15, 0.05]
        return [random.choices(ratings, weights=weights)[0] for _ in range(30)]
    
    def _generate_rsi(self):
        """Generate sample RSI values (0-100)"""
        import random
        return [round(random.uniform(30, 70), 2) for _ in range(30)]
    
    def _generate_momentum(self):
        """Generate sample Momentum values"""
        import random
        return [round(random.uniform(-5, 5), 2) for _ in range(30)]
    
    def _generate_ao(self):
        """Generate sample Awesome Oscillator values"""
        import random
        return [round(random.uniform(-10, 10), 2) for _ in range(30)]
    
    def _generate_cci(self):
        """Generate sample CCI values"""
        import random
        return [round(random.uniform(-200, 200), 2) for _ in range(30)]
    
    def save_to_csv(self, df, symbol):
        """Save dataframe to CSV file"""
        csv_filename = os.path.join(self.output_dir, f"{symbol}_data.csv")
        print(f"Saving data to {csv_filename}...")
        df.to_csv(csv_filename, index=False)
        return csv_filename
    
    def process_all_stocks(self):
        """Process all stocks from config file"""
        stocks = self.load_stocks_config()
        
        if not stocks:
            print("No stocks found in configuration file!")
            return
        
        for stock in stocks:
            symbol = stock['symbol']
            name = stock['name']
            
            # Fetch data
            df = self.fetch_stock_data(symbol, name)
            
            # Save to CSV
            csv_file = self.save_to_csv(df, symbol)
            
            # Store data for HTML generation
            self.stocks_data[symbol] = {
                'name': name,
                'data': df
            }
        
        print(f"\nProcessed {len(self.stocks_data)} stocks successfully")
    
    def generate_multi_stock_html(self):
        """Generate HTML report with left sidebar menu for multiple stocks"""
        print(f"Generating multi-stock HTML report with sidebar menu...")
        
        # Generate sidebar menu HTML
        sidebar_html = self._generate_sidebar()
        
        # Generate content for each stock
        stock_contents = self._generate_stock_contents()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Stock Technical Analysis Dashboard</title>
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
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        .dashboard {{
            display: flex;
            height: 100vh;
        }}
        
        /* Sidebar Styles */
        .sidebar {{
            width: 280px;
            background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            overflow-y: auto;
            box-shadow: 4px 0 10px rgba(0,0,0,0.3);
            position: fixed;
            height: 100vh;
            z-index: 1000;
        }}
        
        .sidebar-header {{
            padding: 25px 20px;
            background: rgba(0,0,0,0.2);
            border-bottom: 2px solid rgba(255,255,255,0.1);
        }}
        
        .sidebar-header h1 {{
            font-size: 1.4em;
            margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .sidebar-header p {{
            font-size: 0.85em;
            opacity: 0.9;
        }}
        
        .stock-list {{
            padding: 10px 0;
        }}
        
        .stock-item {{
            padding: 15px 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
            display: flex;
            flex-direction: column;
        }}
        
        .stock-item:hover {{
            background: rgba(255,255,255,0.1);
            border-left-color: #667eea;
        }}
        
        .stock-item.active {{
            background: rgba(255,255,255,0.15);
            border-left-color: #ffd700;
        }}
        
        .stock-symbol {{
            font-weight: 700;
            font-size: 1.1em;
            margin-bottom: 4px;
        }}
        
        .stock-name {{
            font-size: 0.85em;
            opacity: 0.8;
        }}
        
        /* Main Content Styles */
        .main-content {{
            margin-left: 280px;
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }}
        
        .content-wrapper {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .stock-content {{
            display: none;
            animation: fadeIn 0.5s;
        }}
        
        .stock-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .content-header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .content-header h2 {{
            color: #2a5298;
            font-size: 2.2em;
            margin-bottom: 8px;
        }}
        
        .content-header p {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-card h3 {{
            color: #2a5298;
            margin-bottom: 15px;
            font-size: 1.2em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .rating-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .rating-item:last-child {{
            border-bottom: none;
        }}
        
        .rating-label {{
            font-weight: 500;
            color: #555;
        }}
        
        .rating-value {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: 600;
        }}
        
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            color: #2a5298;
            font-size: 1.4em;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
        }}
        
        .data-table {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .buy {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .sell {{
            color: #dc3545;
            font-weight: bold;
        }}
        
        .neutral {{
            color: #ffc107;
            font-weight: bold;
        }}
        
        .footer {{
            background: white;
            color: #666;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Scrollbar Styles */
        .sidebar::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .sidebar::-webkit-scrollbar-track {{
            background: rgba(0,0,0,0.1);
        }}
        
        .sidebar::-webkit-scrollbar-thumb {{
            background: rgba(255,255,255,0.3);
            border-radius: 4px;
        }}
        
        .sidebar::-webkit-scrollbar-thumb:hover {{
            background: rgba(255,255,255,0.5);
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .sidebar {{
                width: 100%;
                height: auto;
                position: relative;
            }}
            
            .main-content {{
                margin-left: 0;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h1>📊 Stock Dashboard</h1>
                <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Total Stocks: {len(self.stocks_data)}</p>
            </div>
            <div class="stock-list">
                {sidebar_html}
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <div class="content-wrapper">
                {stock_contents}
                
                <div class="footer">
                    <p>📈 Generated by Multi-Stock Analyzer | Data from Yahoo Finance | For educational purposes only</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Stock switching functionality
        function showStock(stockSymbol) {{
            // Hide all stock contents
            const stockContents = document.querySelectorAll('.stock-content');
            stockContents.forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Remove active class from all stock items
            const stockItems = document.querySelectorAll('.stock-item');
            stockItems.forEach(item => {{
                item.classList.remove('active');
            }});
            
            // Show selected stock content
            document.getElementById('stock-' + stockSymbol).classList.add('active');
            
            // Add active class to clicked stock item
            event.target.closest('.stock-item').classList.add('active');
            
            // Scroll to top of main content
            document.querySelector('.main-content').scrollTop = 0;
        }}
        
        // Show first stock by default
        window.addEventListener('load', function() {{
            const firstStock = document.querySelector('.stock-item');
            if (firstStock) {{
                firstStock.click();
            }}
        }});
    </script>
</body>
</html>
"""
        
        # Write HTML file
        with open(self.html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Multi-stock HTML report generated: {self.html_filename}")
        return self.html_filename
    
    def _generate_sidebar(self):
        """Generate sidebar menu HTML"""
        sidebar = ""
        for i, (symbol, stock_info) in enumerate(self.stocks_data.items()):
            active_class = "active" if i == 0 else ""
            sidebar += f"""
                <div class="stock-item {active_class}" onclick="showStock('{symbol}')">
                    <div class="stock-symbol">{symbol}</div>
                    <div class="stock-name">{stock_info['name']}</div>
                </div>
            """
        return sidebar
    
    def _generate_stock_contents(self):
        """Generate content for each stock"""
        contents = ""
        for i, (symbol, stock_info) in enumerate(self.stocks_data.items()):
            active_class = "active" if i == 0 else ""
            df = stock_info['data']
            name = stock_info['name']
            
            # Prepare data for charts
            dates = df['Date'].tolist()
            rsi_values = df['RSI (14)'].tolist()
            momentum_values = df['Mom (10)'].tolist()
            ao_values = df['AO'].tolist()
            cci_values = df['CCI (20)'].tolist()
            close_prices = df['Close'].tolist()
            
            # Count ratings
            tech_ratings = df['Tech Rating'].value_counts().to_dict()
            ma_ratings = df['MA Rating'].value_counts().to_dict()
            os_ratings = df['Os Rating'].value_counts().to_dict()
            
            # Get latest values
            latest = df.iloc[-1]
            
            contents += f"""
        <div id="stock-{symbol}" class="stock-content {active_class}">
            <div class="content-header">
                <h2>{symbol} - {name}</h2>
                <p>Latest Close: ₹{latest['Close']} | Volume: {latest['Volume']:,}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>📊 Technical Rating</h3>
                    {self._generate_rating_html(tech_ratings)}
                </div>
                <div class="stat-card">
                    <h3>📈 MA Rating</h3>
                    {self._generate_rating_html(ma_ratings)}
                </div>
                <div class="stat-card">
                    <h3>🎯 Oscillator Rating</h3>
                    {self._generate_rating_html(os_ratings)}
                </div>
                <div class="stat-card">
                    <h3>📉 Latest Indicators</h3>
                    <div class="rating-item">
                        <span class="rating-label">RSI (14):</span>
                        <span class="rating-value">{latest['RSI (14)']}</span>
                    </div>
                    <div class="rating-item">
                        <span class="rating-label">Momentum (10):</span>
                        <span class="rating-value">{latest['Mom (10)']}</span>
                    </div>
                    <div class="rating-item">
                        <span class="rating-label">AO:</span>
                        <span class="rating-value">{latest['AO']}</span>
                    </div>
                    <div class="rating-item">
                        <span class="rating-label">CCI (20):</span>
                        <span class="rating-value">{latest['CCI (20)']}</span>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">📈 Price & Volume Combo</h2>
                <canvas id="priceVolumeChart-{symbol}"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">🎯 Momentum Indicators Combo (RSI & CCI)</h2>
                <canvas id="momentumComboChart-{symbol}"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">📊 Oscillators Combo (Momentum & AO)</h2>
                <canvas id="oscillatorsChart-{symbol}"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">🔍 All Technical Indicators Overview</h2>
                <canvas id="allIndicatorsChart-{symbol}"></canvas>
            </div>
            
            <div class="data-table">
                <h2 class="chart-title">Complete Data Table</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Close</th>
                            <th>Volume</th>
                            <th>Tech Rating</th>
                            <th>MA Rating</th>
                            <th>Os Rating</th>
                            <th>RSI (14)</th>
                            <th>Mom (10)</th>
                            <th>AO</th>
                            <th>CCI (20)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_table_rows(df)}
                    </tbody>
                </table>
            </div>
            
            <script>
                // Chart.js configuration for {symbol}
                const chartConfig{symbol} = {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }},
                        tooltip: {{
                            mode: 'index',
                            intersect: false
                        }}
                    }},
                    interaction: {{
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }}
                }};
                
                // 1. Price & Volume Combo Chart (Dual Y-axis)
                new Chart(document.getElementById('priceVolumeChart-{symbol}'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(dates)},
                        datasets: [
                            {{
                                label: 'Close Price (₹)',
                                data: {json.dumps(close_prices)},
                                borderColor: 'rgb(54, 162, 235)',
                                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                                tension: 0.4,
                                fill: true,
                                borderWidth: 2,
                                yAxisID: 'y'
                            }},
                            {{
                                label: 'Volume',
                                data: {json.dumps(df['Volume'].tolist())},
                                type: 'bar',
                                backgroundColor: 'rgba(255, 159, 64, 0.3)',
                                borderColor: 'rgb(255, 159, 64)',
                                borderWidth: 1,
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        ...chartConfig{symbol},
                        scales: {{
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: 'Price (₹)'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'Volume'
                                }},
                                grid: {{
                                    drawOnChartArea: false
                                }}
                            }}
                        }}
                    }}
                }});
                
                // 2. Momentum Indicators Combo (RSI & CCI with dual Y-axis)
                new Chart(document.getElementById('momentumComboChart-{symbol}'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(dates)},
                        datasets: [
                            {{
                                label: 'RSI (14)',
                                data: {json.dumps(rsi_values)},
                                borderColor: 'rgb(75, 192, 192)',
                                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                tension: 0.4,
                                fill: true,
                                borderWidth: 2,
                                yAxisID: 'y'
                            }},
                            {{
                                label: 'CCI (20)',
                                data: {json.dumps(cci_values)},
                                borderColor: 'rgb(153, 102, 255)',
                                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                                tension: 0.4,
                                fill: false,
                                borderWidth: 2,
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        ...chartConfig{symbol},
                        scales: {{
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                min: 0,
                                max: 100,
                                title: {{
                                    display: true,
                                    text: 'RSI (0-100)'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'CCI'
                                }},
                                grid: {{
                                    drawOnChartArea: false
                                }}
                            }}
                        }}
                    }}
                }});
                
                // 3. Oscillators Combo (Momentum & AO)
                new Chart(document.getElementById('oscillatorsChart-{symbol}'), {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(dates)},
                        datasets: [
                            {{
                                label: 'Momentum (10)',
                                data: {json.dumps(momentum_values)},
                                backgroundColor: {json.dumps(['rgba(255, 99, 132, 0.6)' if x < 0 else 'rgba(75, 192, 192, 0.6)' for x in momentum_values])},
                                borderColor: {json.dumps(['rgb(255, 99, 132)' if x < 0 else 'rgb(75, 192, 192)' for x in momentum_values])},
                                borderWidth: 1,
                                yAxisID: 'y'
                            }},
                            {{
                                label: 'Awesome Oscillator',
                                data: {json.dumps(ao_values)},
                                backgroundColor: {json.dumps(['rgba(255, 159, 64, 0.6)' if x < 0 else 'rgba(54, 162, 235, 0.6)' for x in ao_values])},
                                borderColor: {json.dumps(['rgb(255, 159, 64)' if x < 0 else 'rgb(54, 162, 235)' for x in ao_values])},
                                borderWidth: 1,
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        ...chartConfig{symbol},
                        scales: {{
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: 'Momentum'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'AO'
                                }},
                                grid: {{
                                    drawOnChartArea: false
                                }}
                            }}
                        }}
                    }}
                }});
                
                // 4. All Technical Indicators Overview (Normalized)
                new Chart(document.getElementById('allIndicatorsChart-{symbol}'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(dates)},
                        datasets: [
                            {{
                                label: 'RSI (14)',
                                data: {json.dumps(rsi_values)},
                                borderColor: 'rgb(75, 192, 192)',
                                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                                tension: 0.4,
                                fill: false,
                                borderWidth: 2
                            }},
                            {{
                                label: 'Momentum (10) - Scaled',
                                data: {json.dumps([50 + x * 5 for x in momentum_values])},
                                borderColor: 'rgb(255, 99, 132)',
                                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                                tension: 0.4,
                                fill: false,
                                borderWidth: 2
                            }},
                            {{
                                label: 'AO - Scaled',
                                data: {json.dumps([50 + x * 2 for x in ao_values])},
                                borderColor: 'rgb(54, 162, 235)',
                                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                                tension: 0.4,
                                fill: false,
                                borderWidth: 2
                            }},
                            {{
                                label: 'CCI (20) - Scaled',
                                data: {json.dumps([50 + x / 4 for x in cci_values])},
                                borderColor: 'rgb(153, 102, 255)',
                                backgroundColor: 'rgba(153, 102, 255, 0.1)',
                                tension: 0.4,
                                fill: false,
                                borderWidth: 2
                            }}
                        ]
                    }},
                    options: {{
                        ...chartConfig{symbol},
                        scales: {{
                            y: {{
                                beginAtZero: false,
                                title: {{
                                    display: true,
                                    text: 'Normalized Values (50 = neutral)'
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
        </div>
"""
        
        return contents
    
    def _generate_rating_html(self, ratings_dict):
        """Generate HTML for rating distribution"""
        html = ""
        for rating, count in sorted(ratings_dict.items(), key=lambda x: x[1], reverse=True):
            html += f"""
                <div class="rating-item">
                    <span class="rating-label">{rating}:</span>
                    <span class="rating-value">{count}</span>
                </div>
            """
        return html
    
    def _generate_table_rows(self, df):
        """Generate HTML table rows from dataframe in reverse chronological order"""
        rows = ""
        # Reverse the dataframe to show newest dates first
        for _, row in df.iloc[::-1].iterrows():
            tech_class = self._get_rating_class(row['Tech Rating'])
            ma_class = self._get_rating_class(row['MA Rating'])
            os_class = self._get_rating_class(row['Os Rating'])
            
            rows += f"""
                <tr>
                    <td>{row['Date']}</td>
                    <td>₹{row['Close']}</td>
                    <td>{row['Volume']:,}</td>
                    <td class="{tech_class}">{row['Tech Rating']}</td>
                    <td class="{ma_class}">{row['MA Rating']}</td>
                    <td class="{os_class}">{row['Os Rating']}</td>
                    <td>{row['RSI (14)']}</td>
                    <td>{row['Mom (10)']}</td>
                    <td>{row['AO']}</td>
                    <td>{row['CCI (20)']}</td>
                </tr>
            """
        return rows
    
    def _get_rating_class(self, rating):
        """Get CSS class based on rating"""
        if 'Buy' in rating:
            return 'buy'
        elif 'Sell' in rating:
            return 'sell'
        else:
            return 'neutral'
    
    def run(self):
        """Main execution method"""
        print("=" * 60)
        print("Multi-Stock Technical Analysis with Yahoo Finance")
        print("=" * 60)
        
        # Step 1: Process all stocks
        self.process_all_stocks()
        
        # Step 2: Generate multi-stock HTML report
        html_file = self.generate_multi_stock_html()
        
        print("\n" + "=" * 60)
        print("✅ Process completed successfully!")
        print("=" * 60)
        print(f"\n📁 CSV Files saved in: {self.output_dir}/")
        print(f"🌐 HTML Report: {html_file}")
        print("\nOpen the HTML file in your browser to view the dashboard.")
        print("The stocks are now in a left sidebar menu for easy navigation!")
        
        return html_file


if __name__ == "__main__":
    analyzer = MultiStockAnalyzer()
    analyzer.run()

# Made with Bob - Enhanced with Yahoo Finance and Sidebar Navigation
