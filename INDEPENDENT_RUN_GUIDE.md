# 🚀 Independent Run Guide - Stock Analysis Platform

## Complete Step-by-Step Guide to Run This Project

---

## 📋 Prerequisites

### Required Software
- **Python 3.8+** (You have Python 3.13 with Anaconda ✅)
- **pip** (Python package manager)
- **Terminal/Command Prompt**

### Check Your Setup
```bash
python --version    # Should show Python 3.8 or higher
pip --version       # Should show pip version
```

---

## 🎯 QUICK START (5 Minutes)

### Step 1: Open Terminal
```bash
# Navigate to project directory
cd /Users/mananranjan/Desktop/Hackathon/StockAnalysis
```

### Step 2: Install Required Packages
```bash
# Install all dependencies at once
pip install streamlit pandas plotly yfinance prophet numpy scipy
```

### Step 3: Run the Application
```bash
# Start the Predictions page
streamlit run frontend/pages/2_🔮_Predictions.py
```

### Step 4: Open in Browser
- The application will automatically open at: **http://localhost:8501**
- Or manually open: http://localhost:8501

**That's it! You're running! 🎉**

---

## 📚 DETAILED SETUP (If Quick Start Doesn't Work)

### Method 1: Using pip (Recommended)

#### Step 1: Navigate to Project
```bash
cd /Users/mananranjan/Desktop/Hackathon/StockAnalysis
```

#### Step 2: Install Dependencies One by One
```bash
# Core packages
pip install streamlit
pip install pandas
pip install numpy
pip install plotly

# Data fetching
pip install yfinance

# Prediction models
pip install prophet

# Scientific computing
pip install scipy
```

#### Step 3: Verify Installation
```bash
python -c "import streamlit; print('✓ Streamlit installed')"
python -c "import pandas; print('✓ Pandas installed')"
python -c "import prophet; print('✓ Prophet installed')"
python -c "import yfinance; print('✓ yfinance installed')"
```

### Method 2: Using requirements.txt

#### Step 1: Navigate to Frontend Directory
```bash
cd /Users/mananranjan/Desktop/Hackathon/StockAnalysis/frontend
```

#### Step 2: Install from Requirements File
```bash
pip install -r requirements.txt
```

---

## 🎮 RUNNING THE APPLICATION

### Option A: Run Home Page (Main Dashboard)
```bash
cd /Users/mananranjan/Desktop/Hackathon/StockAnalysis
streamlit run frontend/Home.py
```
**Access at:** http://localhost:8501

### Option B: Run Predictions Page Directly
```bash
cd /Users/mananranjan/Desktop/Hackathon/StockAnalysis
streamlit run frontend/pages/2_🔮_Predictions.py
```
**Access at:** http://localhost:8501

### Option C: Run Live Dashboard
```bash
cd /Users/mananranjan/Desktop/Hackathon/StockAnalysis
streamlit run frontend/pages/1_📊_Live_Dashboard.py
```
**Access at:** http://localhost:8501

### Option D: Run Multiple Pages Simultaneously
```bash
# Terminal 1 - Home Page
streamlit run frontend/Home.py --server.port 8501

# Terminal 2 - Predictions (in new terminal)
streamlit run frontend/pages/2_🔮_Predictions.py --server.port 8502

# Terminal 3 - Live Dashboard (in new terminal)
streamlit run frontend/pages/1_📊_Live_Dashboard.py --server.port 8503
```

**Access at:**
- Home: http://localhost:8501
- Predictions: http://localhost:8502
- Live Dashboard: http://localhost:8503

---

## 🧪 TESTING THE APPLICATION

### Test 1: Prophet Predictions
1. Open http://localhost:8501
2. Navigate to "🔮 Predictions" page
3. Select stock: **HDFCBANK**
4. Choose period: **30 days**
5. Click **"Generate Predictions"**
6. ✅ You should see a price forecast chart

### Test 2: Monte Carlo Simulation
1. Scroll down to "Monte Carlo Risk Analysis"
2. Select stock: **RELIANCE**
3. Set simulations: **1000**
4. Set days: **30**
5. Click **"Run Simulation"**
6. ✅ You should see probability distribution

### Test 3: Live Dashboard
1. Open http://localhost:8501
2. Navigate to "📊 Live Dashboard"
3. View watchlist with stocks
4. ✅ Should show real-time data

### Test 4: Data Fallback
```bash
# Run test script
python test_predictions_fallback.py
```
✅ Should show successful data loading for 5 stocks

---

## 📊 AVAILABLE FEATURES

### ✅ Working Features (No Backend Required)

1. **Prophet Price Predictions**
   - 7, 30, 90 day forecasts
   - Confidence intervals
   - Interactive charts

2. **Monte Carlo Risk Analysis**
   - 1000+ simulations
   - Probability distributions
   - VaR and risk metrics

3. **Live Dashboard**
   - Real-time price updates
   - Technical indicators
   - Watchlist management

4. **Data Fallback System**
   - Yahoo Finance (primary)
   - Local CSV files (fallback)
   - 22 stocks available offline

### 🔧 Advanced Features (Require Backend Setup)

1. WebSocket Real-time Streaming
2. Database Storage (PostgreSQL)
3. Redis Caching
4. Celery Background Tasks
5. User Authentication

---

## 📈 AVAILABLE STOCKS

### Banking & Finance
- HDFCBANK, ICICIBANK, SBIN, PFC

### Technology
- INFY, TCS

### Energy & Oil
- RELIANCE, IOC, OIL, GAIL

### Metals & Mining
- TATASTEEL, SAIL, VEDL

### Automobiles
- TATAMOTORS

### Infrastructure
- LT, IRCTC

### Consumer Goods
- ITC, HINDUNILVR, ASIANPAINT

### Conglomerates
- ADANIENT, ADANIPOWER, JIOFIN

**Total: 22 stocks with offline data available**

---

## 🛠️ TROUBLESHOOTING

### Problem 1: "Module not found" Error
```bash
# Solution: Install the missing package
pip install <package-name>

# Example:
pip install streamlit
pip install prophet
```

### Problem 2: "Port already in use"
```bash
# Solution: Kill the process using the port
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run frontend/Home.py --server.port 8504
```

### Problem 3: "Could not fetch data"
**Causes:**
- Internet connection issue
- Stock symbol incorrect
- Market closed

**Solutions:**
1. Check internet connection
2. Use correct stock symbols (e.g., HDFCBANK, not HDFC)
3. System will automatically use local CSV files as fallback

### Problem 4: Streamlit Won't Start
```bash
# Solution 1: Reinstall Streamlit
pip uninstall streamlit
pip install streamlit

# Solution 2: Clear Streamlit cache
rm -rf ~/.streamlit

# Solution 3: Use Python module syntax
python -m streamlit run frontend/Home.py
```

### Problem 5: Prophet Installation Fails
```bash
# For macOS with Anaconda:
conda install -c conda-forge prophet

# For pip:
pip install prophet

# If still fails, install dependencies first:
pip install pystan
pip install prophet
```

### Problem 6: Page Shows Blank
**Solutions:**
1. Clear browser cache (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
2. Try incognito/private mode
3. Check terminal for errors
4. Restart Streamlit server

---

## 🔄 STOPPING THE APPLICATION

### Stop Streamlit Server
```bash
# Method 1: In the terminal running Streamlit
Press Ctrl+C

# Method 2: Kill all Streamlit processes
pkill -f streamlit

# Method 3: Kill specific port
lsof -ti:8501 | xargs kill -9
```

---

## 📝 DAILY WORKFLOW

### Starting Your Day
```bash
# 1. Open Terminal
cd /Users/mananranjan/Desktop/Hackathon/StockAnalysis

# 2. Start the application
streamlit run frontend/Home.py

# 3. Open browser to http://localhost:8501

# 4. Start analyzing stocks!
```

### Ending Your Day
```bash
# 1. In terminal, press Ctrl+C to stop Streamlit

# 2. Or close the terminal window
```

---

## 🎯 COMMON USE CASES

### Use Case 1: Quick Price Prediction
```bash
# 1. Start app
streamlit run frontend/pages/2_🔮_Predictions.py

# 2. Select HDFCBANK
# 3. Choose 30 days
# 4. Click Generate
# 5. View forecast
```

### Use Case 2: Risk Analysis
```bash
# 1. Start app
streamlit run frontend/pages/2_🔮_Predictions.py

# 2. Scroll to Monte Carlo section
# 3. Select RELIANCE
# 4. Run 1000 simulations
# 5. View risk metrics
```

### Use Case 3: Monitor Multiple Stocks
```bash
# 1. Start app
streamlit run frontend/pages/1_📊_Live_Dashboard.py

# 2. View watchlist
# 3. Add/remove stocks
# 4. Check technical indicators
```

---

## 📦 PACKAGE VERSIONS (Tested & Working)

```
streamlit >= 1.28.0
pandas >= 2.0.0
numpy >= 1.24.0
plotly >= 5.17.0
yfinance >= 0.2.28
prophet >= 1.1.4
scipy >= 1.11.0
```

---

## 🚀 PERFORMANCE TIPS

### Faster Loading
1. Use local CSV files when market is closed
2. Reduce prediction period for faster results
3. Lower Monte Carlo simulations (500 instead of 1000)

### Better Predictions
1. Use 60-90 days of historical data
2. Include seasonality for long-term predictions
3. Run multiple simulations for better accuracy

---

## 📞 GETTING HELP

### Check Logs
```bash
# Streamlit logs are shown in terminal
# Look for error messages in red

# Common error patterns:
# - "ModuleNotFoundError" → Install missing package
# - "Port already in use" → Kill process or use different port
# - "Could not fetch data" → Check internet or use fallback
```

### Test Individual Components
```bash
# Test data fetching
python test_predictions_fallback.py

# Test Python imports
python -c "import streamlit, pandas, prophet; print('All imports OK')"
```

---

## ✅ VERIFICATION CHECKLIST

Before running, verify:
- [ ] Python 3.8+ installed
- [ ] All packages installed (streamlit, pandas, prophet, yfinance, plotly, numpy, scipy)
- [ ] In correct directory (/Users/mananranjan/Desktop/Hackathon/StockAnalysis)
- [ ] Port 8501 is available
- [ ] Internet connection active (for live data)

---

## 🎉 SUCCESS INDICATORS

You'll know it's working when you see:
- ✅ Terminal shows "You can now view your Streamlit app in your browser"
- ✅ Browser opens automatically to http://localhost:8501
- ✅ Home page loads with navigation menu
- ✅ Can select stocks and generate predictions
- ✅ Charts display correctly
- ✅ No error messages in terminal

---

## 📚 ADDITIONAL RESOURCES

### Documentation Files
- `COMPLETE_SETUP_GUIDE.txt` - Comprehensive setup guide
- `README.md` - Project overview
- `REALTIME_PLATFORM_README.md` - Platform architecture
- `HOW_TO_RUN.md` - Quick start guide

### Test Files
- `test_predictions_fallback.py` - Test data fetching
- `test_data_fetch.py` - Test data sources

---

## 🎓 LEARNING PATH

### Beginner
1. Start with Home page
2. Explore Predictions page
3. Try different stocks
4. Experiment with time periods

### Intermediate
1. Understand Prophet predictions
2. Run Monte Carlo simulations
3. Analyze risk metrics
4. Compare multiple stocks

### Advanced
1. Modify prediction parameters
2. Add custom indicators
3. Integrate new data sources
4. Deploy to cloud

---

## 🔐 SECURITY NOTES

- No authentication required for local use
- Data fetched from public APIs (Yahoo Finance)
- No sensitive data stored
- Safe to use on local machine

---

## 💡 PRO TIPS

1. **Bookmark the URL**: Save http://localhost:8501 for quick access
2. **Use Keyboard Shortcuts**: Cmd+R (Mac) or Ctrl+R (Windows) to refresh
3. **Multiple Tabs**: Open different pages in separate browser tabs
4. **Save Predictions**: Take screenshots of important forecasts
5. **Compare Stocks**: Open multiple browser windows to compare

---

## 🎯 FINAL CHECKLIST

Ready to run? Check these:
- [x] Python installed
- [x] Packages installed
- [x] In project directory
- [x] Terminal open
- [x] Internet connected
- [x] Ready to analyze stocks!

---

## 🚀 LET'S GO!

```bash
# Copy and paste this command to start:
cd /Users/mananranjan/Desktop/Hackathon/StockAnalysis && streamlit run frontend/Home.py
```

**Your stock analysis platform is ready! Happy Trading! 📈**

---

*Last Updated: 2026-05-16*
*Version: 1.0*
*Status: Production Ready ✅*