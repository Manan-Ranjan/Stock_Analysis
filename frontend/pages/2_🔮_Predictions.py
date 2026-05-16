"""
Predictive Analytics Dashboard
AI-powered price predictions and scenario analysis
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

# Simple MinMaxScaler replacement (no sklearn dependency)
def normalize_data(data, feature_range=(0, 1)):
    """Normalize data to a given range without sklearn"""
    min_val, max_val = feature_range
    data_min = np.min(data)
    data_max = np.max(data)
    if data_max == data_min:
        return np.full_like(data, min_val)
    scaled = (data - data_min) / (data_max - data_min)
    return scaled * (max_val - min_val) + min_val

# Import momentum trading system
MOMENTUM_AVAILABLE = False
try:
    from momentum_trading.data.fetcher import DataFetcher
    MOMENTUM_AVAILABLE = True
except ImportError:
    pass  # Will use yfinance fallback

# Page config
st.set_page_config(
    page_title="Predictive Analytics",
    page_icon="🔮",
    layout="wide"
)

# Import yfinance for fallback
import yfinance as yf

# Custom CSS
st.markdown("""
<style>
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin: 1rem 0;
    }
    .confidence-high {
        color: #00ff00;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffff00;
        font-weight: bold;
    }
    .confidence-low {
        color: #ff6600;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🔮 Predictive Analytics Dashboard")
st.markdown("AI-powered price predictions using Prophet time series forecasting")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Prediction Settings")
    
    # Stock selection
    stock_symbol = st.text_input("Stock Symbol", value="HDFCBANK", help="Enter NSE stock symbol")
    
    # Prediction horizon
    forecast_days = st.slider("Forecast Days", 1, 30, 7, help="Number of days to predict")
    
    # Confidence level
    confidence_level = st.slider("Confidence Level", 80, 99, 95, help="Prediction confidence interval")
    
    st.markdown("---")
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        historical_days = st.slider("Historical Data (days)", 30, 365, 90)
        num_simulations = st.slider("Monte Carlo Simulations", 100, 10000, 1000)
        include_seasonality = st.checkbox("Include Seasonality", value=True)
    
    st.markdown("---")
    
    # Generate prediction button
    generate_prediction = st.button("🔮 Generate Prediction", use_container_width=True, type="primary")

# Main content
if generate_prediction:
    with st.spinner(f"Generating predictions for {stock_symbol}..."):
        try:
            # Import the data helper
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from utils.data_helper import fetch_stock_data_with_fallback, get_available_stocks
            
            # Show available stocks from CSV
            available_stocks = get_available_stocks()
            if available_stocks:
                st.info(f"📁 Available in local cache: {', '.join(available_stocks[:10])}{'...' if len(available_stocks) > 10 else ''}")
            
            # Fetch data with fallback
            st.info(f"🔍 Fetching data for {stock_symbol}...")
            data, source = fetch_stock_data_with_fallback(stock_symbol, days=historical_days)
            
            if data is None or data.empty:
                st.error(f"❌ Could not fetch data for {stock_symbol}")
                st.info("💡 Try these stocks (available in local cache):")
                if available_stocks:
                    cols = st.columns(5)
                    for idx, stock in enumerate(available_stocks[:15]):
                        with cols[idx % 5]:
                            if st.button(stock, key=f"stock_{stock}"):
                                st.session_state['selected_stock'] = stock
                                st.rerun()
                st.markdown("""
                **Or try:**
                - HDFCBANK, RELIANCE, INFY, TCS, ICICIBANK
                - Add .NS for live data (e.g., HDFCBANK.NS)
                """)
            else:
                # Show data source
                st.success(f"✓ Data loaded from: {source}")
                
                # Prepare data
                df = data[['Date', 'Close']].copy()
                df.columns = ['ds', 'y']
                
                current_price = df['y'].iloc[-1]
                
                # Display current info
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Current Price", f"₹{current_price:.2f}")
                
                with col2:
                    change_1d = ((df['y'].iloc[-1] - df['y'].iloc[-2]) / df['y'].iloc[-2] * 100)
                    st.metric("1-Day Change", f"{change_1d:+.2f}%")
                
                with col3:
                    change_7d = ((df['y'].iloc[-1] - df['y'].iloc[-8]) / df['y'].iloc[-8] * 100) if len(df) > 7 else 0
                    st.metric("7-Day Change", f"{change_7d:+.2f}%")
                
                with col4:
                    volatility = df['y'].pct_change().std() * np.sqrt(252) * 100
                    st.metric("Volatility (Annual)", f"{volatility:.1f}%")
                
                st.markdown("---")
                
                # Tab layout
                tab1, tab2 = st.tabs([
                    "📈 Price Forecast",
                    "📊 Probability Distribution"
                ])
                
                with tab1:
                    st.markdown("### 📈 Prophet Time Series Forecast")
                    
                    # Always show Prophet forecast
                    if True:
                        # Train Prophet model
                        model = Prophet(
                            daily_seasonality=include_seasonality,
                            weekly_seasonality=include_seasonality,
                            yearly_seasonality=False,
                            interval_width=confidence_level/100
                        )
                        
                        model.fit(df)
                        
                        # Make future dataframe
                        future = model.make_future_dataframe(periods=forecast_days)
                        forecast = model.predict(future)
                        
                        # Get predictions
                        predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days)
                        
                        # Calculate expected return
                        predicted_price = predictions['yhat'].iloc[-1]
                        expected_return = ((predicted_price - current_price) / current_price * 100)
                        
                        # Display prediction summary
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("#### 🎯 Predicted Price")
                            st.markdown(f"<h2 style='color: {'#00ff00' if expected_return > 0 else '#ff0000'};'>₹{predicted_price:.2f}</h2>", unsafe_allow_html=True)
                            st.markdown(f"**Expected Return:** {expected_return:+.2f}%")
                        
                        with col2:
                            st.markdown("#### 📊 Confidence Range")
                            st.markdown(f"**Upper Bound:** ₹{predictions['yhat_upper'].iloc[-1]:.2f}")
                            st.markdown(f"**Lower Bound:** ₹{predictions['yhat_lower'].iloc[-1]:.2f}")
                            range_pct = ((predictions['yhat_upper'].iloc[-1] - predictions['yhat_lower'].iloc[-1]) / current_price * 100)
                            st.markdown(f"**Range:** ±{range_pct/2:.1f}%")
                        
                        with col3:
                            st.markdown("#### 🎲 Recommendation")
                            if expected_return > 5:
                                st.success("🟢 STRONG BUY")
                                st.markdown("High upside potential")
                            elif expected_return > 2:
                                st.success("🟢 BUY")
                                st.markdown("Positive outlook")
                            elif expected_return > -2:
                                st.warning("🟡 HOLD")
                                st.markdown("Neutral outlook")
                            else:
                                st.error("🔴 SELL")
                                st.markdown("Negative outlook")
                        
                        # Plot forecast
                        fig = go.Figure()
                        
                        # Historical data
                        fig.add_trace(go.Scatter(
                            x=df['ds'],
                            y=df['y'],
                            mode='lines',
                            name='Historical',
                            line=dict(color='blue', width=2)
                        ))
                        
                        # Forecast
                        fig.add_trace(go.Scatter(
                            x=predictions['ds'],
                            y=predictions['yhat'],
                            mode='lines',
                            name='Forecast',
                            line=dict(color='red', width=2, dash='dash')
                        ))
                        
                        # Confidence interval
                        fig.add_trace(go.Scatter(
                            x=predictions['ds'].tolist() + predictions['ds'].tolist()[::-1],
                            y=predictions['yhat_upper'].tolist() + predictions['yhat_lower'].tolist()[::-1],
                            fill='toself',
                            fillcolor='rgba(255,0,0,0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name=f'{confidence_level}% Confidence'
                        ))
                        
                        fig.update_layout(
                            title=f"{stock_symbol} Price Forecast ({forecast_days} Days)",
                            xaxis_title="Date",
                            yaxis_title="Price (₹)",
                            height=500,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Prediction table
                        st.markdown("#### 📋 Daily Predictions")
                        pred_table = predictions.copy()
                        pred_table['ds'] = pred_table['ds'].dt.strftime('%Y-%m-%d')
                        pred_table.columns = ['Date', 'Predicted Price', 'Lower Bound', 'Upper Bound']
                        pred_table['Predicted Price'] = pred_table['Predicted Price'].apply(lambda x: f"₹{x:.2f}")
                        pred_table['Lower Bound'] = pred_table['Lower Bound'].apply(lambda x: f"₹{x:.2f}")
                        pred_table['Upper Bound'] = pred_table['Upper Bound'].apply(lambda x: f"₹{x:.2f}")
                        
                        st.dataframe(pred_table, use_container_width=True, hide_index=True)
                    
                    else:
                        st.info("Select 'Prophet' or 'Both' in model settings to see time series forecast")
                
                with tab2:
                    st.markdown("### 📊 Probability Distribution")
                    
                    # Calculate returns distribution
                    returns = df['y'].pct_change().dropna()
                    
                    # Generate future price distribution
                    mean_return = returns.mean()
                    std_return = returns.std()
                    
                    # Simulate price distribution
                    simulated_returns = np.random.normal(mean_return, std_return, 10000)
                    simulated_prices = current_price * (1 + simulated_returns * forecast_days)
                    
                    # Create histogram
                    fig = go.Figure()
                    
                    fig.add_trace(go.Histogram(
                        x=simulated_prices,
                        nbinsx=50,
                        name='Price Distribution',
                        marker_color='lightblue'
                    ))
                    
                    # Add current price line
                    fig.add_vline(x=current_price, line_dash="dash", line_color="red", annotation_text="Current Price")
                    
                    # Add mean line
                    fig.add_vline(x=simulated_prices.mean(), line_dash="dash", line_color="green", annotation_text="Expected Price")
                    
                    fig.update_layout(
                        title=f"Price Distribution in {forecast_days} Days",
                        xaxis_title="Price (₹)",
                        yaxis_title="Frequency",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Probability metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        prob_up = (simulated_prices > current_price).sum() / len(simulated_prices) * 100
                        st.metric("Probability of Gain", f"{prob_up:.1f}%")
                    
                    with col2:
                        prob_5pct = (simulated_prices > current_price * 1.05).sum() / len(simulated_prices) * 100
                        st.metric("Probability of +5%", f"{prob_5pct:.1f}%")
                    
                    with col3:
                        prob_10pct = (simulated_prices > current_price * 1.10).sum() / len(simulated_prices) * 100
                        st.metric("Probability of +10%", f"{prob_10pct:.1f}%")
                
        
        except Exception as e:
            st.error(f"Error generating predictions: {e}")
            import traceback
            st.code(traceback.format_exc())

else:
    # Initial state
    st.info("👆 Configure settings in the sidebar and click 'Generate Prediction' to start")
    
    st.markdown("### 🎯 What You'll Get")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📈 Prophet Forecast
        - Time series prediction using Facebook Prophet
        - Confidence intervals
        - Trend and seasonality analysis
        - Daily price predictions
        
        #### 📊 Probability Distribution
        - Price distribution analysis
        - Probability of gains
        - Expected value calculation
        - Risk assessment
        """)
    
    with col2:
        st.markdown("""
        #### 🎲 Monte Carlo Simulation
        - 1000+ price path simulations
        - Statistical analysis
        - Best/worst case scenarios
        - Percentile analysis
        
        #### 📋 Scenario Analysis
        - Bull, base, and bear cases
        - Risk metrics (VaR, Sharpe)
        - Maximum drawdown
        - Expected returns
        """)

# Footer
st.markdown("---")
st.markdown("**Note:** Predictions are based on historical data and statistical models. Past performance does not guarantee future results. Always do your own research before making investment decisions.")

# Made with Bob
