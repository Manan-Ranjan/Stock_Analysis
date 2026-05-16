"""
HDFC Bank Stock Technical Analysis Data Fetcher and HTML Generator
Now integrated with multi-source data fetcher (Google Finance + Yahoo Finance)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from bs4 import BeautifulSoup
import yfinance as yf
import ta

# Import the multi-source data fetcher
try:
    from data_fetcher import DataFetcher, DataSourceConfig
    MULTI_SOURCE_AVAILABLE = True
except ImportError:
    MULTI_SOURCE_AVAILABLE = False
    print("Warning: data_fetcher not available, using fallback method")

class HDFCStockAnalyzer:
    def __init__(self, use_multi_source=True, primary_source='yahoo', fallback_source='google'):
        self.symbol = "HDFCBANK"
        self.csv_filename = "hdfc_bank_data.csv"
        self.html_filename = "hdfc_bank_trends.html"
        self.use_multi_source = use_multi_source and MULTI_SOURCE_AVAILABLE
        
        if self.use_multi_source:
            print(f"🔄 Using multi-source data fetcher (Primary: {primary_source.upper()}, Fallback: {fallback_source.upper()})")
            self.data_fetcher = DataFetcher(primary_source=primary_source, fallback_source=fallback_source)
        else:
            print("📊 Using direct Yahoo Finance API")
        
    def fetch_stock_data(self):
        """
        Fetch HDFC Bank stock data with technical indicators
        Now uses multi-source fetcher with Google Finance and Yahoo Finance
        """
        print("Fetching HDFC Bank stock data...")
        
        if self.use_multi_source:
            # Use the multi-source data fetcher
            return self._fetch_with_multi_source()
        else:
            # Fallback to direct Yahoo Finance
            return self._fetch_with_yahoo_direct()
    
    def _fetch_with_multi_source(self):
        """Fetch data using multi-source fetcher"""
        try:
            # Fetch raw data
            raw_data = self.data_fetcher.fetch_stock_data(self.symbol, 'NSE', days=90)
            
            if raw_data is None or raw_data.empty:
                print("  ⚠️ Multi-source fetch failed, using sample data")
                return self._generate_sample_data()
            
            # Keep last 30 days
            raw_data = raw_data.tail(30).copy()
            
            # Calculate technical indicators
            df = self._calculate_indicators(raw_data)
            
            print(f"  ✓ Successfully fetched and processed {len(df)} days of data")
            print(f"  📊 Data source: {raw_data['Source'].iloc[0]}")
            
            return df
            
        except Exception as e:
            print(f"  ❌ Error in multi-source fetch: {e}")
            return self._generate_sample_data()
    
    def _fetch_with_yahoo_direct(self):
        """Direct Yahoo Finance fetch (fallback)"""
        try:
            yahoo_symbol = f"{self.symbol}.NS"
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            stock = yf.Ticker(yahoo_symbol)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                return self._generate_sample_data()
            
            df = df.tail(30).copy()
            df = df.reset_index()
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            df['Symbol'] = self.symbol
            
            return self._calculate_indicators(df)
            
        except Exception as e:
            print(f"  ❌ Error in Yahoo fetch: {e}")
            return self._generate_sample_data()
    
    def _calculate_indicators(self, df):
        """Calculate technical indicators from raw OHLCV data"""
        try:
            # Ensure we have the required columns
            if 'Close' not in df.columns:
                return self._generate_sample_data()
            
            # Calculate RSI
            df['RSI (14)'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
            
            # Calculate Momentum
            df['Mom (10)'] = ta.momentum.ROCIndicator(df['Close'], window=10).roc()
            
            # Calculate Awesome Oscillator
            if 'High' in df.columns and 'Low' in df.columns:
                ao = ta.momentum.AwesomeOscillatorIndicator(df['High'], df['Low'])
                df['AO'] = ao.awesome_oscillator()
            else:
                df['AO'] = 0
            
            # Calculate CCI
            if 'High' in df.columns and 'Low' in df.columns:
                df['CCI (20)'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=20).cci()
            else:
                df['CCI (20)'] = 0
            
            # Calculate Moving Averages for ratings
            df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
            df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
            df['EMA_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()
            
            # Generate ratings
            df['Tech Rating'] = df.apply(self._calculate_tech_rating, axis=1)
            df['MA Rating'] = df.apply(self._calculate_ma_rating, axis=1)
            df['Os Rating'] = df.apply(self._calculate_oscillator_rating, axis=1)
            
            # Prepare final dataframe
            result_df = pd.DataFrame({
                'Date': df['Date'] if 'Date' in df.columns else df.index.strftime('%Y-%m-%d'),
                'Symbol': self.symbol,
                'Name': 'HDFC Bank Ltd',
                'Tech Rating': df['Tech Rating'],
                'MA Rating': df['MA Rating'],
                'Os Rating': df['Os Rating'],
                'RSI (14)': df['RSI (14)'].round(2),
                'Mom (10)': df['Mom (10)'].round(2),
                'AO': df['AO'].round(2),
                'CCI (20)': df['CCI (20)'].round(2)
            })
            
            return result_df
            
        except Exception as e:
            print(f"  ⚠️ Error calculating indicators: {e}")
            return self._generate_sample_data()
    
    def _calculate_tech_rating(self, row):
        """Calculate technical rating based on indicators"""
        try:
            score = 0
            if 'RSI (14)' in row and not pd.isna(row['RSI (14)']):
                if row['RSI (14)'] > 70:
                    score -= 2
                elif row['RSI (14)'] > 60:
                    score -= 1
                elif row['RSI (14)'] < 30:
                    score += 2
                elif row['RSI (14)'] < 40:
                    score += 1
            
            if 'Mom (10)' in row and not pd.isna(row['Mom (10)']):
                if row['Mom (10)'] > 5:
                    score += 1
                elif row['Mom (10)'] < -5:
                    score -= 1
            
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
        except:
            return 'Neutral'
    
    def _calculate_ma_rating(self, row):
        """Calculate MA rating"""
        try:
            if 'Close' in row and 'SMA_20' in row and not pd.isna(row['SMA_20']):
                if row['Close'] > row['SMA_20']:
                    return 'Buy'
                elif row['Close'] < row['SMA_20']:
                    return 'Sell'
            return 'Neutral'
        except:
            return 'Neutral'
    
    def _calculate_oscillator_rating(self, row):
        """Calculate oscillator rating"""
        try:
            score = 0
            if 'RSI (14)' in row and not pd.isna(row['RSI (14)']):
                if row['RSI (14)'] < 30:
                    score += 2
                elif row['RSI (14)'] < 40:
                    score += 1
                elif row['RSI (14)'] > 70:
                    score -= 2
                elif row['RSI (14)'] > 60:
                    score -= 1
            
            if 'CCI (20)' in row and not pd.isna(row['CCI (20)']):
                if row['CCI (20)'] < -100:
                    score += 1
                elif row['CCI (20)'] > 100:
                    score -= 1
            
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
        except:
            return 'Neutral'
    
    def _generate_sample_data(self):
        """Generate sample data as fallback"""
        print("  ℹ️ Using sample data")
        dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
        
        data = {
            'Date': dates,
            'Symbol': [self.symbol] * 30,
            'Name': ['HDFC Bank Ltd'] * 30,
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
    
    def save_to_csv(self, df):
        """Save dataframe to CSV file"""
        print(f"Saving data to {self.csv_filename}...")
        df.to_csv(self.csv_filename, index=False)
        print(f"Data saved successfully to {self.csv_filename}")
        return self.csv_filename
    
    def generate_html_report(self, csv_file):
        """Generate HTML report with trend visualization"""
        print(f"Generating HTML report from {csv_file}...")
        
        # Read CSV data
        df = pd.read_csv(csv_file)
        
        # Prepare data for charts
        dates = df['Date'].tolist()
        rsi_values = df['RSI (14)'].tolist()
        momentum_values = df['Mom (10)'].tolist()
        ao_values = df['AO'].tolist()
        cci_values = df['CCI (20)'].tolist()
        
        # Count ratings
        tech_ratings = df['Tech Rating'].value_counts().to_dict()
        ma_ratings = df['MA Rating'].value_counts().to_dict()
        os_ratings = df['Os Rating'].value_counts().to_dict()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HDFC Bank - Technical Analysis Trends</title>
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
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
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
            font-size: 1.2em;
        }}
        
        .rating-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .rating-item:last-child {{
            border-bottom: none;
        }}
        
        .rating-label {{
            font-weight: 500;
        }}
        
        .rating-value {{
            background: #667eea;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.9em;
        }}
        
        .charts-section {{
            padding: 30px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            color: #2a5298;
            font-size: 1.5em;
            margin-bottom: 20px;
            text-align: center;
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
            background: #2a5298;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 HDFC Bank - Technical Analysis Dashboard</h1>
            <p>Symbol: HDFCBANK | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 Technical Rating Distribution</h3>
                {self._generate_rating_html(tech_ratings)}
            </div>
            <div class="stat-card">
                <h3>📈 MA Rating Distribution</h3>
                {self._generate_rating_html(ma_ratings)}
            </div>
            <div class="stat-card">
                <h3>🎯 Oscillator Rating Distribution</h3>
                {self._generate_rating_html(os_ratings)}
            </div>
            <div class="stat-card">
                <h3>📉 Latest Indicators</h3>
                <div class="rating-item">
                    <span class="rating-label">RSI (14):</span>
                    <span class="rating-value">{rsi_values[-1]}</span>
                </div>
                <div class="rating-item">
                    <span class="rating-label">Momentum (10):</span>
                    <span class="rating-value">{momentum_values[-1]}</span>
                </div>
                <div class="rating-item">
                    <span class="rating-label">AO:</span>
                    <span class="rating-value">{ao_values[-1]}</span>
                </div>
                <div class="rating-item">
                    <span class="rating-label">CCI (20):</span>
                    <span class="rating-value">{cci_values[-1]}</span>
                </div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <h2 class="chart-title">RSI (14) Trend - 30 Days</h2>
                <canvas id="rsiChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">Momentum (10) Trend - 30 Days</h2>
                <canvas id="momentumChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">Awesome Oscillator (AO) Trend - 30 Days</h2>
                <canvas id="aoChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">CCI (20) Trend - 30 Days</h2>
                <canvas id="cciChart"></canvas>
            </div>
        </div>
        
        <div class="data-table">
            <h2 class="chart-title">Complete Data Table</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Symbol</th>
                        <th>Name</th>
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
        
        <div class="footer">
            <p>Generated by HDFC Stock Analyzer | Data for educational purposes only</p>
        </div>
    </div>
    
    <script>
        // Chart.js configuration
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
        
        // RSI Chart
        new Chart(document.getElementById('rsiChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'RSI (14)',
                    data: {json.dumps(rsi_values)},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                ...chartConfig,
                scales: {{
                    y: {{
                        beginAtZero: false,
                        min: 0,
                        max: 100
                    }}
                }}
            }}
        }});
        
        // Momentum Chart
        new Chart(document.getElementById('momentumChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'Momentum (10)',
                    data: {json.dumps(momentum_values)},
                    backgroundColor: {json.dumps(['rgba(255, 99, 132, 0.5)' if x < 0 else 'rgba(75, 192, 192, 0.5)' for x in momentum_values])},
                    borderColor: {json.dumps(['rgb(255, 99, 132)' if x < 0 else 'rgb(75, 192, 192)' for x in momentum_values])},
                    borderWidth: 1
                }}]
            }},
            options: chartConfig
        }});
        
        // AO Chart
        new Chart(document.getElementById('aoChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'Awesome Oscillator',
                    data: {json.dumps(ao_values)},
                    backgroundColor: {json.dumps(['rgba(255, 99, 132, 0.5)' if x < 0 else 'rgba(75, 192, 192, 0.5)' for x in ao_values])},
                    borderColor: {json.dumps(['rgb(255, 99, 132)' if x < 0 else 'rgb(75, 192, 192)' for x in ao_values])},
                    borderWidth: 1
                }}]
            }},
            options: chartConfig
        }});
        
        // CCI Chart
        new Chart(document.getElementById('cciChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'CCI (20)',
                    data: {json.dumps(cci_values)},
                    borderColor: 'rgb(153, 102, 255)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                ...chartConfig,
                scales: {{
                    y: {{
                        beginAtZero: false
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        
        # Write HTML file
        with open(self.html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report generated successfully: {self.html_filename}")
        return self.html_filename
    
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
                    <td>{row['Symbol']}</td>
                    <td>{row['Name']}</td>
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
        print("HDFC Bank Stock Technical Analysis")
        print("=" * 60)
        
        # Step 1: Fetch data
        df = self.fetch_stock_data()
        print(f"\nFetched {len(df)} records")
        
        # Step 2: Save to CSV
        csv_file = self.save_to_csv(df)
        
        # Step 3: Generate HTML report
        html_file = self.generate_html_report(csv_file)
        
        print("\n" + "=" * 60)
        print("✅ Process completed successfully!")
        print("=" * 60)
        print(f"\n📄 CSV File: {csv_file}")
        print(f"🌐 HTML Report: {html_file}")
        print("\nOpen the HTML file in your browser to view the trends.")
        
        return csv_file, html_file


if __name__ == "__main__":
    analyzer = HDFCStockAnalyzer()
    analyzer.run()

# Made with Bob
