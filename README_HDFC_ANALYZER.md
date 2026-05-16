# HDFC Bank Stock Technical Analysis Tool

## Overview
This Python program fetches HDFC Bank stock technical analysis data and generates interactive HTML visualizations with trend charts.

## Features
- ✅ Fetches technical indicators for HDFC Bank (HDFCBANK)
- ✅ Saves data to CSV format
- ✅ Generates interactive HTML dashboard with:
  - Technical Rating, MA Rating, and Oscillator Rating distributions
  - RSI (14) trend chart
  - Momentum (10) trend chart
  - Awesome Oscillator (AO) trend chart
  - CCI (20) trend chart
  - Complete data table with all indicators

## Data Fields
The program collects the following technical indicators:
- **Date**: Trading date
- **Symbol**: Stock symbol (HDFCBANK)
- **Name**: Company name (HDFC Bank Ltd)
- **Tech Rating**: Overall technical rating (Strong Buy, Buy, Neutral, Sell, Strong Sell)
- **MA Rating**: Moving Average rating
- **Os Rating**: Oscillator rating
- **RSI (14)**: Relative Strength Index (14-period)
- **Mom (10)**: Momentum indicator (10-period)
- **AO**: Awesome Oscillator
- **CCI (20)**: Commodity Channel Index (20-period)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Install Dependencies
```bash
pip install -r hdfc_requirements.txt
```

Or install manually:
```bash
pip install pandas requests beautifulsoup4 lxml
```

## Usage

### Run the Analyzer
```bash
python3 hdfc_stock_analyzer.py
```

### Output Files
The program generates two files:
1. **hdfc_bank_data.csv** - Raw data in CSV format
2. **hdfc_bank_trends.html** - Interactive HTML dashboard

### View Results
Open `hdfc_bank_trends.html` in your web browser to view:
- Interactive trend charts
- Rating distributions
- Complete data table
- Latest indicator values

## File Structure
```
.
├── hdfc_stock_analyzer.py      # Main Python script
├── hdfc_requirements.txt       # Python dependencies
├── hdfc_bank_data.csv         # Generated CSV data (output)
├── hdfc_bank_trends.html      # Generated HTML report (output)
└── README_HDFC_ANALYZER.md    # This file
```

## Customization

### Modify Data Source
The current implementation generates sample data. To fetch real data from the internet:

1. **Option 1: Yahoo Finance API**
   ```python
   import yfinance as yf
   ticker = yf.Ticker("HDFCBANK.NS")
   data = ticker.history(period="1mo")
   ```

2. **Option 2: Alpha Vantage API**
   ```python
   import requests
   API_KEY = "your_api_key"
   url = f"https://www.alphavantage.co/query?function=RSI&symbol=HDFCBANK&interval=daily&apikey={API_KEY}"
   ```

3. **Option 3: Web Scraping**
   - TradingView
   - Investing.com
   - NSE/BSE official websites

### Modify Time Period
Edit the `fetch_stock_data()` method in `hdfc_stock_analyzer.py`:
```python
# Change from 30 days to 60 days
dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') 
         for x in range(60, 0, -1)]
```

### Customize HTML Styling
Modify the CSS in the `generate_html_report()` method to change:
- Colors
- Fonts
- Layout
- Chart types

## Technical Indicators Explained

### RSI (Relative Strength Index)
- Range: 0-100
- Overbought: > 70
- Oversold: < 30
- Neutral: 30-70

### Momentum
- Positive values: Upward momentum
- Negative values: Downward momentum
- Zero: No momentum

### Awesome Oscillator (AO)
- Positive: Bullish momentum
- Negative: Bearish momentum

### CCI (Commodity Channel Index)
- > +100: Overbought
- < -100: Oversold
- -100 to +100: Normal range

## Troubleshooting

### Import Error: pandas not found
```bash
pip install pandas
```

### Permission Denied
```bash
chmod +x hdfc_stock_analyzer.py
```

### Python Command Not Found
Use `python3` instead of `python`:
```bash
python3 hdfc_stock_analyzer.py
```

## Future Enhancements
- [ ] Real-time data fetching from financial APIs
- [ ] Multiple stock symbols support
- [ ] Email alerts for specific conditions
- [ ] Export to PDF
- [ ] Historical data comparison
- [ ] Machine learning predictions
- [ ] Mobile-responsive design

## Notes
- Current implementation uses sample data for demonstration
- For production use, integrate with real financial data APIs
- Always verify data accuracy before making investment decisions
- This tool is for educational purposes only

## License
MIT License - Feel free to modify and use as needed

## Support
For issues or questions, please refer to the code comments or create an issue in the repository.

---
**Disclaimer**: This tool is for educational and informational purposes only. It does not constitute financial advice. Always consult with a qualified financial advisor before making investment decisions.