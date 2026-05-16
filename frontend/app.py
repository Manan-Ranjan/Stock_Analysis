"""
Real-Time Stock Analysis Platform - Home Page
Main dashboard with live market data and real-time updates
"""

import streamlit as st
import sys
import os

# Add parent directory to path to import momentum_trading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Real-Time Stock Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-online {
        color: #00ff00;
        font-weight: bold;
    }
    .status-offline {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📈 Real-Time Stock Analysis Platform</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Stock+Analysis", use_column_width=True)
    st.markdown("---")
    
    st.markdown("### 🎯 Quick Navigation")
    st.markdown("""
    - 📊 **Live Dashboard** - Real-time market data
    - 🔮 **Predictions** - AI-powered forecasts
    - 📈 **Analysis** - Technical indicators
    - 💼 **Portfolio** - Track your investments
    - 🎮 **Paper Trading** - Practice trading
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    # Backend URL configuration
    backend_url = st.text_input(
        "Backend URL",
        value=os.getenv("BACKEND_URL", "http://localhost:8000"),
        help="URL of the backend API server"
    )
    
    ws_url = st.text_input(
        "WebSocket URL",
        value=os.getenv("WS_URL", "ws://localhost:8000"),
        help="WebSocket URL for real-time updates"
    )
    
    # Store in session state
    st.session_state['backend_url'] = backend_url
    st.session_state['ws_url'] = ws_url
    
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🌐 System Status",
        value="Online",
        delta="All systems operational"
    )

with col2:
    st.metric(
        label="📊 Active Connections",
        value="0",
        delta="WebSocket connections"
    )

with col3:
    st.metric(
        label="📈 Stocks Monitored",
        value="22",
        delta="NIFTY stocks"
    )

with col4:
    st.metric(
        label="🔄 Update Frequency",
        value="5s",
        delta="Real-time streaming"
    )

st.markdown("---")

# Feature cards
st.markdown("## 🚀 Platform Features")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown("### 📊 Live Market Pulse")
        st.markdown("""
        - Real-time price updates
        - Market sentiment analysis
        - Sector rotation tracking
        - Volume analysis
        - Momentum scanner
        """)
        if st.button("Open Live Dashboard", key="live_dash", use_container_width=True):
            st.switch_page("pages/1_📊_Live_Dashboard.py")

with col2:
    with st.container():
        st.markdown("### 🔮 Predictive Analytics")
        st.markdown("""
        - AI-powered price predictions
        - Probability distributions
        - Scenario analysis
        - Monte Carlo simulations
        - Confidence intervals
        """)
        if st.button("Open Predictions", key="predictions", use_container_width=True):
            st.switch_page("pages/2_🔮_Predictions.py")

with col3:
    with st.container():
        st.markdown("### 📈 Technical Analysis")
        st.markdown("""
        - RSI, MACD, SuperTrend
        - Momentum indicators
        - Volume analysis
        - Support/Resistance
        - Pattern recognition
        """)
        if st.button("Open Analysis", key="analysis", use_container_width=True):
            st.switch_page("pages/3_📈_Analysis.py")

st.markdown("---")

# Quick stats
st.markdown("## 📊 Quick Stats")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Today's Top Movers")
    
    # Sample data (will be replaced with real data)
    top_movers = pd.DataFrame({
        'Symbol': ['INFY', 'TCS', 'HDFCBANK', 'RELIANCE', 'ICICIBANK'],
        'Price': ['₹1,450', '₹3,890', '₹1,645', '₹2,890', '₹1,120'],
        'Change': ['+3.2%', '+2.8%', '+2.1%', '+1.8%', '+1.5%'],
        'Signal': ['🟢 BUY', '🟢 BUY', '🟢 BUY', '🟡 HOLD', '🟢 BUY']
    })
    
    st.dataframe(
        top_movers,
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.markdown("### 📉 Sector Performance")
    
    sector_perf = pd.DataFrame({
        'Sector': ['IT', 'Banking', 'Energy', 'FMCG', 'Auto'],
        'Change': ['+2.5%', '+1.8%', '+1.2%', '+0.5%', '-0.3%'],
        'Trend': ['📈', '📈', '📈', '➡️', '📉']
    })
    
    st.dataframe(
        sector_perf,
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# Getting started
st.markdown("## 🎓 Getting Started")

with st.expander("📖 How to Use This Platform"):
    st.markdown("""
    ### Step 1: Connect to Backend
    1. Ensure the backend server is running at `http://localhost:8000`
    2. Check the WebSocket connection status in the sidebar
    3. Configure URLs in Settings if needed
    
    ### Step 2: Explore Features
    - **Live Dashboard**: Monitor real-time market data
    - **Predictions**: View AI-powered price forecasts
    - **Analysis**: Analyze stocks with technical indicators
    - **Portfolio**: Track your investments
    - **Paper Trading**: Practice trading strategies
    
    ### Step 3: Add Stocks to Watchlist
    1. Go to Live Dashboard
    2. Search for stocks
    3. Click "Add to Watchlist"
    4. Receive real-time updates
    
    ### Step 4: Get Trading Signals
    - System automatically generates BUY/SELL signals
    - Based on momentum, trend, and volume analysis
    - Confidence scores provided for each signal
    
    ### Step 5: Test Strategies
    - Use Paper Trading to test strategies
    - No real money involved
    - Track performance metrics
    - Refine your approach
    """)

with st.expander("🔧 System Requirements"):
    st.markdown("""
    ### Backend Services
    - ✅ FastAPI Server (Port 8000)
    - ✅ PostgreSQL Database (Port 5432)
    - ✅ Redis Cache (Port 6379)
    - ✅ WebSocket Server (Port 8000)
    
    ### Data Sources
    - Yahoo Finance (Primary)
    - Google Finance (Fallback)
    - NSE Data (Optional)
    
    ### Features Status
    - ✅ Real-time streaming
    - ✅ Technical indicators
    - ✅ Signal generation
    - ✅ Backtesting
    - 🔄 Predictive analytics (In Progress)
    - 🔄 Paper trading (In Progress)
    """)

with st.expander("📚 Documentation"):
    st.markdown("""
    ### Available Documentation
    - [Architecture Overview](../REALTIME_PLATFORM_ARCHITECTURE.md)
    - [Setup Guide](../SETUP_GUIDE.md)
    - [API Documentation](http://localhost:8000/docs)
    - [WebSocket Protocol](../REALTIME_PLATFORM_ARCHITECTURE.md#websocket-protocol)
    
    ### Quick Links
    - Backend API: http://localhost:8000
    - API Docs: http://localhost:8000/docs
    - WebSocket: ws://localhost:8000/api/v1/ws
    - Celery Flower: http://localhost:5555
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Real-Time Stock Analysis Platform v1.0.0</p>
    <p>Built with ❤️ using FastAPI, Streamlit, and your Momentum Trading System</p>
    <p>© 2026 | <a href='http://localhost:8000/docs'>API Docs</a> | <a href='https://github.com'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)

# Made with Bob
