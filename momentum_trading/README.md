# Momentum Trading System

A comprehensive Python-based momentum trading application for Indian stock markets with multi-source data fetching, technical analysis, and automated buy/sell signal generation.

## 🌟 Key Features

### Data Sources
- **NSEpy** (Primary) - NSE India data with Open Interest support
- **Yahoo Finance** - Extensive historical data
- **Finnhub API** - Professional-grade data
- **Google Finance** - Real-time prices

### Technical Indicators
- **Momentum**: RSI, ROC, Stochastic, Williams %R, MACD, CCI, TSI
- **Trend**: SuperTrend, Moving Averages (SMA/EMA/WMA), ADX, Aroon, PSAR
- **Volatility**: ATR, Bollinger Bands, Keltner Channels
- **Volume**: OBV, Volume Profile, VWAP
- **Open Interest**: Futures & Options OI analysis

### Signal Generation
- Multi-indicator confluence
- Momentum-based entry/exit signals
- Trend confirmation
- Volume validation
- Open Interest analysis

### Risk Management
- Position sizing based on ATR
- Dynamic stop loss
- Take profit targets
- Risk-reward ratio calculation

### Backtesting
- Historical performance analysis
- Strategy optimization
- Performance metrics (Sharpe, Sortino, Max Drawdown)

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
# Navigate to momentum_trading directory
cd momentum_trading

# Install all requirements
pip install -r requirements.txt
```

### Optional: Install TA-Lib (Advanced Technical Analysis)

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ta-lib
pip install TA-Lib
```

**Windows:**
Download pre-built wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)

## 🚀 Quick Start

### 1. Basic Stock Data Fetching

```python
from momentum_trading.data import DataFetcher

# Initialize with NSEpy as primary source
fetcher = DataFetcher(primary_source='nsepy', fallback_source='yahoo')

# Fetch stock data
data = fetcher.fetch_stock_data('HDFCBANK', exchange='NSE', days=90)
print(data.head())
```

### 2. Fetch Data with Open Interest

```python
# Fetch futures data with Open Interest
oi_data = fetcher.fetch_with_open_interest('RELIANCE', days=30)

# Get OI analysis
oi_analysis = fetcher.get_oi_analysis('RELIANCE')
print(f"Signal: {oi_analysis['signal']}")
print(f"Type: {oi_analysis['interpretation']['type']}")
```

### 3. Calculate Technical Indicators

```python
from momentum_trading.indicators import MomentumIndicators, TrendIndicators

# Add momentum indicators
data_with_momentum = MomentumIndicators.add_all_momentum_indicators(data)

# Add trend indicators
data_with_trends = TrendIndicators.add_all_trend_indicators(data_with_momentum)

# View indicators
print(data_with_trends[['Date', 'Close', 'RSI', 'SuperTrend', 'Momentum_Score']].tail())
```

### 4. Generate Trading Signals

```python
from momentum_trading.signals import SignalGenerator, MomentumStrategy

# Initialize signal generator
signal_gen = SignalGenerator(strategy=MomentumStrategy())

# Generate signals
signals = signal_gen.generate_signals(data_with_trends)

# View signals
print(signals[signals['Signal'] != 'Hold'])
```

## 📊 NSEpy Integration

### Why NSEpy?

NSEpy is specifically designed for Indian stock markets and provides:

1. **Accurate NSE Data**: Direct from NSE India
2. **Open Interest**: Futures and Options OI data
3. **Deliverable Volume**: Delivery percentage data
4. **Index Data**: NIFTY, BANKNIFTY, sector indices
5. **Corporate Actions**: Dividends, splits, bonuses

### NSEpy Features

#### Stock Data
```python
from momentum_trading.data import NSEDataFetcher

nse = NSEDataFetcher()

# Fetch stock data
stock_data = nse.fetch_stock_data('HDFCBANK', days=30)
print(stock_data[['Date', 'Close', 'Volume', 'Deliverable_Volume', 'Deliverable_Pct']].tail())
```

#### Futures with Open Interest
```python
# Fetch futures data
futures_data = nse.fetch_futures_data('RELIANCE', days=30)
print(futures_data[['Date', 'Close', 'OI', 'OI_Change', 'OI_Change_Pct']].tail())
```

#### Open Interest Analysis
```python
# Get OI interpretation
oi_analysis = nse.get_oi_analysis('RELIANCE')

# Interpretation rules:
# Price ↑ + OI ↑ = Long Build-up (Bullish)
# Price ↓ + OI ↑ = Short Build-up (Bearish)
# Price ↑ + OI ↓ = Short Covering (Bullish)
# Price ↓ + OI ↓ = Long Unwinding (Bearish)

print(f"Signal: {oi_analysis['signal']}")
print(f"Type: {oi_analysis['interpretation']['type']}")
print(f"Description: {oi_analysis['interpretation']['description']}")
```

#### Index Data
```python
# Fetch NIFTY data
nifty_data = nse.fetch_index_data('NIFTY', days=30)

# Fetch BANKNIFTY data
banknifty_data = nse.fetch_index_data('BANKNIFTY', days=30)
```

#### Options Data
```python
# Fetch call option data
call_data = nse.fetch_options_data(
    symbol='RELIANCE',
    strike_price=2500,
    option_type='CE',
    days=30
)

# Fetch put option data
put_data = nse.fetch_options_data(
    symbol='RELIANCE',
    strike_price=2500,
    option_type='PE',
    days=30
)
```

## 🎯 Momentum Trading Strategy

### Entry Signals (BUY)

1. **Trend Confirmation**
   - SuperTrend is bullish (direction = 1)
   - Price > EMA(20)
   - ADX > 25 (strong trend)

2. **Momentum Confirmation**
   - RSI > 50 and rising
   - ROC > 0
   - MACD > Signal line
   - Momentum Score > 60

3. **Volume Validation**
   - Volume > 20-day average
   - Deliverable percentage > 50% (NSEpy)

4. **Open Interest (Futures)**
   - Price rising + OI rising = Long Build-up

### Exit Signals (SELL)

1. **Trend Reversal**
   - SuperTrend turns bearish
   - Price < EMA(20)

2. **Momentum Loss**
   - RSI < 50 and falling
   - ROC < 0
   - Momentum Score < 40

3. **Stop Loss Hit**
   - Price < (Entry - 2*ATR)

4. **Take Profit**
   - Price > (Entry + 3*ATR)

### Signal Scoring

```python
Signal Score = (
    Trend Score (0-30) +
    Momentum Score (0-30) +
    Volume Score (0-20) +
    OI Score (0-20)
) / 100

Score >= 80: Strong Buy
Score >= 60: Buy
Score >= 40: Hold
Score >= 20: Sell
Score < 20: Strong Sell
```

## 📁 Project Structure

```
momentum_trading/
├── __init__.py
├── README.md
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── strategy_config.py
├── data/
│   ├── __init__.py
│   ├── fetcher.py              # Unified data fetcher
│   ├── nse_fetcher.py          # NSEpy integration
│   ├── cache.py
│   └── validator.py
├── indicators/
│   ├── __init__.py
│   ├── momentum.py             # RSI, ROC, Stochastic, etc.
│   ├── trend.py                # SuperTrend, MA, ADX, etc.
│   ├── volatility.py           # ATR, Bollinger Bands, etc.
│   ├── volume.py               # Volume indicators
│   └── composite.py            # Composite indicators
├── signals/
│   ├── __init__.py
│   ├── generator.py            # Signal generation
│   ├── momentum_strategy.py    # Momentum strategy
│   ├── filters.py
│   └── scorer.py
├── risk/
│   ├── __init__.py
│   ├── position_sizing.py
│   ├── stop_loss.py
│   └── portfolio.py
├── backtest/
│   ├── __init__.py
│   ├── engine.py
│   ├── metrics.py
│   └── optimizer.py
├── reporting/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── alerts.py
│   └── logger.py
└── utils/
    ├── __init__.py
    ├── helpers.py
    └── constants.py
```

## 🔧 Configuration

### Strategy Configuration

```python
# config/strategy_config.py
STRATEGY_CONFIG = {
    # Momentum Indicators
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'roc_period': 10,
    'stochastic_period': 14,
    
    # Trend Indicators
    'supertrend_period': 10,
    'supertrend_multiplier': 3.0,
    'ema_fast': 12,
    'ema_slow': 26,
    'adx_period': 14,
    'adx_threshold': 25,
    
    # Risk Management
    'stop_loss_atr_multiplier': 2.0,
    'take_profit_atr_multiplier': 3.0,
    'position_size_risk_percent': 2.0,
    'max_portfolio_risk': 10.0,
    
    # Signal Thresholds
    'strong_buy_score': 80,
    'buy_score': 60,
    'sell_score': 40,
    'strong_sell_score': 20
}
```

### Data Source Configuration

```python
# config/settings.py
DATA_CONFIG = {
    'primary_source': 'nsepy',      # nsepy, yahoo, finnhub, google
    'fallback_source': 'yahoo',
    'exchange': 'NSE',
    'historical_days': 90,
    'cache_enabled': True,
    'cache_duration_hours': 1
}
```

## 📈 Example: Complete Workflow

```python
from momentum_trading.data import DataFetcher
from momentum_trading.indicators import MomentumIndicators, TrendIndicators
from momentum_trading.signals import SignalGenerator, MomentumStrategy
from momentum_trading.risk import PositionSizer
from momentum_trading.reporting import DashboardGenerator

# 1. Fetch Data
fetcher = DataFetcher(primary_source='nsepy')
data = fetcher.fetch_stock_data('HDFCBANK', days=90)

# 2. Calculate Indicators
data = MomentumIndicators.add_all_momentum_indicators(data)
data = TrendIndicators.add_all_trend_indicators(data)

# 3. Generate Signals
signal_gen = SignalGenerator(strategy=MomentumStrategy())
signals = signal_gen.generate_signals(data)

# 4. Calculate Position Size
sizer = PositionSizer(account_size=100000, risk_percent=2.0)
position_size = sizer.calculate_position_size(
    entry_price=signals['Entry_Price'].iloc[-1],
    stop_loss=signals['Stop_Loss'].iloc[-1]
)

# 5. Generate Report
dashboard = DashboardGenerator()
dashboard.create_dashboard(data, signals, output_file='report.html')

print(f"Latest Signal: {signals['Signal'].iloc[-1]}")
print(f"Position Size: {position_size} shares")
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=momentum_trading --cov-report=html

# Run specific test
pytest tests/test_indicators.py
```

## 📊 Performance Metrics

The system calculates comprehensive performance metrics:

- **Returns**: Total return, annualized return
- **Risk**: Volatility, max drawdown, downside deviation
- **Risk-Adjusted**: Sharpe ratio, Sortino ratio, Calmar ratio
- **Trade Stats**: Win rate, profit factor, average win/loss
- **Exposure**: Time in market, average holding period

## 🔐 Security

- Store API keys in environment variables
- Use `.env` file for local development
- Never commit API keys to version control

```bash
# .env file
FINNHUB_API_KEY=your_api_key_here
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `/docs` folder
- Examples: See `/examples` folder

## 🙏 Acknowledgments

- **NSEpy**: For providing NSE India data
- **TA-Lib**: For technical analysis functions
- **yfinance**: For Yahoo Finance data
- **Finnhub**: For professional market data

---

**Version**: 1.0.0  
**Last Updated**: 2026-05-14  
**Author**: Bob - AI Software Engineer