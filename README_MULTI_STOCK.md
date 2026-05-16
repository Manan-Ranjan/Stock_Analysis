# Multi-Stock Technical Analysis Dashboard

A comprehensive Python-based stock analysis tool that fetches real-time data from **Yahoo Finance** and generates an interactive HTML dashboard with a **left sidebar menu** for easy navigation.

## 🌟 Features

### Data Source
- **Yahoo Finance Integration**: Fetches real, accurate stock data using the `yfinance` library
- **Real-time Technical Indicators**: RSI, Momentum, Awesome Oscillator, CCI
- **Moving Average Analysis**: SMA and EMA calculations
- **Automated Ratings**: Technical, MA, and Oscillator ratings based on indicator values

### User Interface
- **Left Sidebar Navigation**: Easy-to-use menu with all stocks listed vertically
- **No Scrolling Issues**: Fixed sidebar with scrollable stock list
- **Responsive Design**: Works on desktop and mobile devices
- **Combo/Overlay Charts**: Multiple indicators overlaid on single charts for better comparison
- **Dual Y-Axis Charts**: Compare indicators with different scales side-by-side
- **Interactive Visualizations**: Hover to see all values at once
- **Data Tables**: Complete historical data with color-coded ratings

### Technical Analysis
- **RSI (14)**: Relative Strength Index for momentum analysis
- **Momentum (10)**: Rate of Change indicator
- **Awesome Oscillator**: Market momentum indicator
- **CCI (20)**: Commodity Channel Index
- **Moving Averages**: SMA 20, SMA 50, EMA 20
- **Automated Ratings**: Buy/Sell/Neutral signals based on multiple indicators

## 📋 Prerequisites

- Python 3.7 or higher
- Internet connection (for fetching stock data from Yahoo Finance)

## 🚀 Installation

1. **Install Required Dependencies**:
```bash
pip install -r multi_stock_requirements.txt
```

The requirements include:
- `yfinance` - Yahoo Finance data fetcher
- `pandas` - Data manipulation
- `numpy` - Numerical computations
- `ta` - Technical analysis library
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing

## 📊 Configuration

### Stock Configuration File

Edit `stocks_config.csv` to add or remove stocks:

```csv
Symbol,Name
HDFCBANK,HDFC Bank Ltd
RELIANCE,Reliance Industries Ltd
TCS,Tata Consultancy Services Ltd
INFY,Infosys Ltd
```

**Note**: For Indian stocks (NSE), the script automatically adds `.NS` suffix to fetch data from Yahoo Finance.

## 🎯 Usage

### Run the Analyzer

```bash
python3 multi_stock_analyzer.py
```

### What Happens

1. **Loads Configuration**: Reads stock symbols from `stocks_config.csv`
2. **Fetches Data**: Downloads 90 days of historical data from Yahoo Finance
3. **Calculates Indicators**: Computes RSI, Momentum, AO, CCI, and Moving Averages
4. **Generates Ratings**: Creates Buy/Sell/Neutral ratings based on technical analysis
5. **Saves CSV Files**: Stores data in `stock_data/` directory
6. **Creates HTML Dashboard**: Generates `multi_stock_trends.html` with sidebar navigation

### Output Files

- **CSV Files**: `stock_data/{SYMBOL}_data.csv` - Individual stock data
- **HTML Dashboard**: `multi_stock_trends.html` - Interactive visualization

## 🎨 Dashboard Features

### Left Sidebar Menu
- **Fixed Position**: Always visible while scrolling
- **Stock List**: All stocks displayed vertically
- **Active Indicator**: Highlights currently selected stock
- **Hover Effects**: Visual feedback on mouse hover
- **Scrollable**: Handles large number of stocks

### Main Content Area
- **Stock Header**: Symbol, name, latest price, and volume
- **Statistics Cards**:
  - Technical Rating Distribution
  - MA Rating Distribution
  - Oscillator Rating Distribution
  - Latest Indicator Values
- **Combo/Overlay Charts**:
  - **📈 Price & Volume Combo**: Price line with volume bars (dual Y-axis)
  - **🎯 Momentum Indicators Combo**: RSI and CCI overlaid (dual Y-axis)
  - **📊 Oscillators Combo**: Momentum and AO bars side-by-side (dual Y-axis)
  - **🔍 All Indicators Overview**: All technical indicators normalized and overlaid
- **Data Table**: Complete historical data with color-coded ratings

### Chart Features
- **Dual Y-Axis**: Compare indicators with different scales
- **Interactive Tooltips**: Hover to see all values at once
- **Color Coding**: Positive/negative values in different colors
- **Synchronized X-Axis**: All charts aligned by date
- **Normalized View**: Compare all indicators on same scale

### Color Coding
- 🟢 **Green (Buy)**: Strong Buy, Buy signals
- 🔴 **Red (Sell)**: Strong Sell, Sell signals
- 🟡 **Yellow (Neutral)**: Neutral signals

## 📈 Technical Indicators Explained

### RSI (Relative Strength Index)
- **Range**: 0-100
- **Oversold**: < 30 (potential buy signal)
- **Overbought**: > 70 (potential sell signal)
- **Neutral**: 30-70

### Momentum (Rate of Change)
- **Positive**: Upward price momentum
- **Negative**: Downward price momentum
- **Zero**: No momentum

### Awesome Oscillator (AO)
- **Positive**: Bullish momentum
- **Negative**: Bearish momentum
- **Crossing Zero**: Potential trend change

### CCI (Commodity Channel Index)
- **Above +100**: Overbought condition
- **Below -100**: Oversold condition
- **Between -100 and +100**: Normal range

## 🔧 Customization

### Adding More Stocks

1. Open `stocks_config.csv`
2. Add new rows with Symbol and Name
3. Run the analyzer again

### Changing Time Period

Edit `multi_stock_analyzer.py`:
```python
# Line ~52: Change days for data fetch
start_date = end_date - timedelta(days=90)  # Change 90 to desired days

# Line ~67: Change days for display
df = df.tail(30).copy()  # Change 30 to desired days
```

### Modifying Indicators

The script uses the `ta` library. You can add more indicators:
```python
# Example: Add MACD
from ta.trend import MACD
macd = MACD(df['Close'])
df['MACD'] = macd.macd()
```

## 🐛 Troubleshooting

### No Data Found for Stock
- **Issue**: Yahoo Finance doesn't have data for the symbol
- **Solution**: Check if the symbol is correct or if the stock is delisted
- **Fallback**: Script automatically uses sample data

### Import Errors
- **Issue**: Missing dependencies
- **Solution**: Run `pip install -r multi_stock_requirements.txt`

### Slow Performance
- **Issue**: Fetching data for many stocks takes time
- **Solution**: Reduce number of stocks in `stocks_config.csv`

## 📝 Data Accuracy

### Yahoo Finance
- **Pros**: 
  - Free and reliable
  - Real-time data
  - No API key required
  - Comprehensive historical data
- **Cons**:
  - Rate limiting on excessive requests
  - Occasional data gaps
  - Some stocks may not be available

### Alternative Data Sources

If you need more accuracy or different data sources, you can modify the script to use:
- **Alpha Vantage**: Requires API key, limited free tier
- **Finnhub**: Good for real-time data, requires API key
- **IEX Cloud**: Comprehensive data, paid service
- **NSE/BSE Direct**: For Indian stocks, requires web scraping

## 🎓 Understanding the Ratings

### Technical Rating
Based on RSI and Momentum:
- **Strong Buy**: RSI < 30 and positive momentum
- **Buy**: RSI < 40 or positive momentum
- **Neutral**: Balanced indicators
- **Sell**: RSI > 60 or negative momentum
- **Strong Sell**: RSI > 70 and negative momentum

### MA Rating
Based on price vs moving averages:
- **Strong Buy**: Price above both SMA 20 and SMA 50
- **Buy**: Price above SMA 20
- **Neutral**: Mixed signals
- **Sell**: Price below SMA 20
- **Strong Sell**: Price below both SMA 20 and SMA 50

### Oscillator Rating
Based on RSI and CCI:
- **Buy**: RSI < 30 or CCI < -100 (oversold)
- **Sell**: RSI > 70 or CCI > 100 (overbought)
- **Neutral**: Normal range

## 📊 Sample Output

```
============================================================
Multi-Stock Technical Analysis with Yahoo Finance
============================================================
Loading stocks configuration from stocks_config.csv...
Loaded 22 stocks
Fetching data for HDFCBANK (HDFC Bank Ltd)...
  ✓ Successfully fetched 30 days of data
Saving data to stock_data/HDFCBANK_data.csv...
...
Processed 22 stocks successfully
Generating multi-stock HTML report with sidebar menu...
Multi-stock HTML report generated: multi_stock_trends.html

============================================================
✅ Process completed successfully!
============================================================

📁 CSV Files saved in: stock_data/
🌐 HTML Report: multi_stock_trends.html

Open the HTML file in your browser to view the dashboard.
The stocks are now in a left sidebar menu for easy navigation!
```

## 🔐 Disclaimer

**Important**: This tool is for educational and informational purposes only. 

- Not financial advice
- Past performance doesn't guarantee future results
- Always do your own research
- Consult a financial advisor before making investment decisions
- The author is not responsible for any financial losses

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share feedback

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing free stock data
- **Chart.js** for beautiful interactive charts
- **ta library** for technical analysis calculations
- **yfinance** for easy Yahoo Finance API access

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the code comments
3. Test with a smaller set of stocks first

---

**Made with ❤️ by Bob** - Enhanced with Yahoo Finance and Sidebar Navigation

Last Updated: 2026-04-27