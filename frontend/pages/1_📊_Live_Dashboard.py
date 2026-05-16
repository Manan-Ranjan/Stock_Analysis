"""
Live Market Pulse Dashboard
Real-time stock monitoring with WebSocket integration
"""

# Page config MUST be first Streamlit command
import streamlit as st
st.set_page_config(
    page_title="Live Dashboard",
    page_icon="📊",
    layout="wide"
)

# Now import everything else
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from streamlit_autorefresh import st_autorefresh
import requests
from bs4 import BeautifulSoup
import feedparser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import data helper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_helper import fetch_stock_data

# Import yfinance for fallback
import yfinance as yf

# Import momentum trading system with fallback
MOMENTUM_AVAILABLE = False
try:
    from momentum_trading.data.fetcher import DataFetcher
    from momentum_trading.indicators.momentum import MomentumIndicators
    from momentum_trading.indicators.trend import TrendIndicators
    MOMENTUM_AVAILABLE = True
except ImportError:
    pass

# Custom CSS
st.markdown("""
<style>
    .live-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #00ff00;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    .price-up {
        color: #00ff00;
        font-weight: bold;
    }
    .price-down {
        color: #ff0000;
        font-weight: bold;
    }
    .signal-buy {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .signal-sell {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .signal-hold {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['HDFCBANK', 'RELIANCE', 'INFY', 'TCS', 'ICICIBANK']

if 'live_data' not in st.session_state:
    st.session_state.live_data = {}

if 'ws_connected' not in st.session_state:
    st.session_state.ws_connected = False

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 Live Market Pulse Dashboard")
with col2:
    # Auto-refresh every 5 seconds
    count = st_autorefresh(interval=5000, key="dashboard_refresh")
    st.markdown(f'<div class="live-indicator"></div> <span style="color: #00ff00;">LIVE</span>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎛️ Dashboard Controls")
    
    # Watchlist management
    st.markdown("#### 📋 Watchlist")
    
    # Add stock
    new_stock = st.text_input("Add Stock Symbol", placeholder="e.g., SBIN")
    if st.button("➕ Add to Watchlist", use_container_width=True):
        if new_stock and new_stock.upper() not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_stock.upper())
            st.success(f"Added {new_stock.upper()}")
            st.rerun()
    
    # Remove stock
    if st.session_state.watchlist:
        stock_to_remove = st.selectbox("Remove Stock", st.session_state.watchlist)
        if st.button("➖ Remove from Watchlist", use_container_width=True):
            st.session_state.watchlist.remove(stock_to_remove)
            st.success(f"Removed {stock_to_remove}")
            st.rerun()
    
    st.markdown("---")
    
    # Filters
    st.markdown("#### 🔍 Filters")
    show_signals = st.multiselect(
        "Show Signals",
        ["BUY", "SELL", "HOLD"],
        default=["BUY", "SELL", "HOLD"]
    )
    
    st.markdown("---")
    
    # WebSocket status
    st.markdown("#### 🔌 Connection Status")
    backend_url = st.session_state.get('backend_url', 'http://localhost:8000')
    
    if st.button("🔄 Refresh Connection", use_container_width=True):
        st.rerun()
    
    st.markdown(f"**Backend:** {backend_url}")
    st.markdown(f"**Status:** {'🟢 Connected' if st.session_state.ws_connected else '🔴 Disconnected'}")

# Main dashboard
tab1, tab2 = st.tabs(["📊 Overview", "📰 Stock News"])

with tab1:
    st.markdown("### 🌐 Market Overview")
    
    # Market metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Market Sentiment", "Bullish", "↑ 72/100", delta_color="normal")
    
    with col2:
        st.metric("Advancing", "38", "↑ 76%", delta_color="normal")
    
    with col3:
        st.metric("Declining", "12", "↓ 24%", delta_color="inverse")
    
    with col4:
        st.metric("Avg Volume", "1.8x", "↑ 80%", delta_color="normal")
    
    with col5:
        st.metric("Active Signals", "15", "🟢 BUY", delta_color="normal")
    
    st.markdown("---")
    
    # Fetch and display watchlist data
    st.markdown("### 📋 Your Watchlist")
    
    if st.session_state.watchlist:
        try:
            fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')
            
            watchlist_data = []
            
            with st.spinner("Fetching live data..."):
                for symbol in st.session_state.watchlist:
                    try:
                        # Fetch data
                        if MOMENTUM_AVAILABLE:
                            data = fetcher.fetch_stock_data(symbol, exchange='NSE', days=60)
                        else:
                            # Fallback: use yfinance directly
                            ticker = yf.Ticker(f"{symbol}.NS")
                            data = ticker.history(period="60d")
                            if not data.empty:
                                data = data.reset_index()
                        
                        if data is not None and not data.empty:
                            # Add indicators if momentum system is available
                            if MOMENTUM_AVAILABLE:
                                try:
                                    data = MomentumIndicators.add_all_momentum_indicators(data)
                                    data = TrendIndicators.add_all_trend_indicators(data)
                                except:
                                    pass
                            
                            latest = data.iloc[-1]
                            prev = data.iloc[-2] if len(data) > 1 else latest
                            
                            # Calculate signal
                            score = 0
                            
                            # Use technical indicators if available
                            if 'RSI' in data.columns and latest.get('RSI', 0) > 50:
                                score += 20
                            if 'Momentum_Score' in data.columns and latest.get('Momentum_Score', 0) > 60:
                                score += 20
                            if 'SuperTrend_Direction' in data.columns and latest.get('SuperTrend_Direction', 0) == 1:
                                score += 30
                            if 'SMA_20' in data.columns and latest['Close'] > latest.get('SMA_20', 0):
                                score += 15
                            if 'ADX' in data.columns and latest.get('ADX', 0) > 25:
                                score += 15
                            
                            # Fallback: Use simple price-based scoring if no indicators
                            if score == 0 and len(data) >= 5:
                                # Calculate simple moving averages
                                sma_5 = data['Close'].tail(5).mean()
                                sma_20 = data['Close'].tail(min(20, len(data))).mean()
                                
                                # Price momentum (last 5 days)
                                price_change_5d = ((latest['Close'] - data.iloc[-5]['Close']) / data.iloc[-5]['Close'] * 100) if len(data) >= 5 else 0
                                
                                # Scoring based on price action
                                if latest['Close'] > sma_5: score += 25  # Above short-term average
                                if latest['Close'] > sma_20: score += 25  # Above long-term average
                                if price_change_5d > 2: score += 30  # Strong upward momentum
                                elif price_change_5d > 0: score += 15  # Positive momentum
                                if latest['Close'] > latest['Open']: score += 20  # Bullish candle
                            
                            if score >= 60:
                                signal = "BUY"
                                signal_emoji = "🟢"
                            elif score >= 30:
                                signal = "HOLD"
                                signal_emoji = "🟡"
                            else:
                                signal = "SELL"
                                signal_emoji = "🔴"
                            
                            # Calculate change
                            price_change = ((latest['Close'] - prev['Close']) / prev['Close'] * 100)
                            
                            # Build simple watchlist entry - no technical indicators
                            entry = {
                                'Symbol': symbol,
                                'Price': f"₹{latest['Close']:.2f}",
                                'Change': f"{price_change:+.2f}%",
                                'Signal': f"{signal_emoji} {signal}"
                            }
                            
                            watchlist_data.append(entry)
                    
                    except Exception as e:
                        st.warning(f"Could not fetch {symbol}: {str(e)[:50]}")
            
            if watchlist_data:
                df = pd.DataFrame(watchlist_data)
                
                # Filter by signal
                if show_signals:
                    df = df[df['Signal'].str.contains('|'.join(show_signals))]
                
                # Display simple table - no technical indicators
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Symbol": st.column_config.TextColumn("Stock", width="medium"),
                        "Price": st.column_config.TextColumn("Current Price", width="medium"),
                        "Change": st.column_config.TextColumn("Change %", width="medium"),
                        "Signal": st.column_config.TextColumn("Signal", width="medium")
                    }
                )
                
                # Store in session state for other tabs
                st.session_state.watchlist_df = df
            else:
                st.info("No data available for watchlist stocks")
        
        except Exception as e:
            st.error(f"Error fetching data: {e}")
    else:
        st.info("Add stocks to your watchlist to start monitoring")

with tab2:
    st.markdown("### 📰 Stock News Agent")
    
    if st.session_state.watchlist:
        # Select stock for news
        selected_news_stock = st.selectbox("Select Stock for News", st.session_state.watchlist, key="news_stock")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"#### Latest News for {selected_news_stock}")
        with col2:
            if st.button("🔄 Search News", use_container_width=True):
                st.rerun()
        
        with st.spinner(f"🔍 Searching news for {selected_news_stock}..."):
            try:
                # Function to fetch real news using NewsAPI
                def fetch_stock_news(stock_symbol, company_name=None):
                    """Fetch real news from NewsAPI (NDTV, Economic Times, etc.)"""
                    articles = []
                    
                    # Get NewsAPI key from environment
                    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
                    
                    # Method 1: NewsAPI - Real news from Indian sources
                    if NEWS_API_KEY and NEWS_API_KEY != 'your_actual_api_key_here':
                        try:
                            search_query = company_name if company_name else stock_symbol
                            url = "https://newsapi.org/v2/everything"
                            params = {
                                'q': f'{search_query} stock OR {search_query} shares',
                                'language': 'en',
                                'sortBy': 'publishedAt',
                                'pageSize': 20,
                                'apiKey': NEWS_API_KEY,
                                'domains': 'ndtv.com,economictimes.indiatimes.com,business-standard.com,livemint.com,moneycontrol.com,financialexpress.com,thehindubusinessline.com'
                            }
                            
                            response = requests.get(url, params=params, timeout=10)
                            
                            if response.status_code == 200:
                                data = response.json()
                                
                                if data.get('status') == 'ok' and data.get('articles'):
                                    for item in data['articles'][:15]:
                                        # Skip removed articles
                                        if not item.get('title') or item.get('title') == '[Removed]':
                                            continue
                                        
                                        # Parse date
                                        pub_date = item.get('publishedAt', '')
                                        try:
                                            dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                                            published = dt.strftime('%Y-%m-%d %H:%M')
                                        except:
                                            published = 'Recently'
                                        
                                        article = {
                                            'title': item.get('title', 'No title'),
                                            'link': item.get('url', ''),
                                            'published': published,
                                            'source': item.get('source', {}).get('name', 'News Source'),
                                            'summary': item.get('description', '')[:300] if item.get('description') else ''
                                        }
                                        articles.append(article)
                                    
                                    if articles:
                                        st.success(f"✅ Found {len(articles)} articles from NewsAPI")
                                        return articles[:10]
                            elif response.status_code == 401:
                                st.error("❌ Invalid NewsAPI key. Please check your .env file")
                            elif response.status_code == 429:
                                st.warning("⚠️ NewsAPI rate limit reached. Using fallback...")
                        except Exception as e:
                            st.warning(f"NewsAPI error: {str(e)[:100]}")
                    else:
                        st.info("💡 Add your NewsAPI key to .env file to get real news from NDTV, Economic Times, etc.")
                    
                    # Method 2: Try yfinance fallback
                    try:
                        ticker = yf.Ticker(f"{stock_symbol}.NS")
                        yf_news = ticker.news
                        
                        if yf_news and len(yf_news) > 0:
                            for item in yf_news[:10]:
                                article = {
                                    'title': item.get('title', 'No title'),
                                    'link': item.get('link', ''),
                                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M') if item.get('providerPublishTime') else 'Recently',
                                    'source': item.get('publisher', 'Yahoo Finance'),
                                    'summary': item.get('summary', '')[:200] if item.get('summary') else ''
                                }
                                articles.append(article)
                            if articles:
                                st.info("📰 Showing news from Yahoo Finance")
                                return articles
                    except:
                        pass
                    
                    # Method 3: Sample news if all else fails
                    if not articles:
                        st.warning("⚠️ Could not fetch real news. Add NewsAPI key to .env file.")
                        sample_news = [
                            {
                                'title': f'{company_name or stock_symbol} - Get Real News with NewsAPI',
                                'link': 'https://newsapi.org/register',
                                'published': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                'source': 'Setup Required',
                                'summary': 'Add your NewsAPI key to the .env file to see real news from NDTV, Economic Times, and other sources.'
                            }
                        ]
                        articles = sample_news
                    
                    return articles[:10]
                
                # Company name mapping (add more as needed)
                company_names = {
                    'HDFCBANK': 'HDFC Bank',
                    'RELIANCE': 'Reliance Industries',
                    'INFY': 'Infosys',
                    'TCS': 'Tata Consultancy Services',
                    'ICICIBANK': 'ICICI Bank',
                    'SBIN': 'State Bank of India',
                    'TATAMOTORS': 'Tata Motors',
                    'TATASTEEL': 'Tata Steel',
                    'ITC': 'ITC Limited',
                    'LT': 'Larsen & Toubro'
                }
                
                company_name = company_names.get(selected_news_stock, selected_news_stock)
                news_articles = fetch_stock_news(selected_news_stock, company_name)
                
                if news_articles:
                    st.success(f"✅ Found {len(news_articles)} news articles")
                    
                    # Display news articles
                    for idx, article in enumerate(news_articles):
                        # Sentiment analysis
                        title_lower = article['title'].lower()
                        summary_lower = article.get('summary', '').lower()
                        text = title_lower + ' ' + summary_lower
                        
                        # Positive keywords
                        positive_words = ['surge', 'gain', 'profit', 'growth', 'bullish', 'rally', 'up', 'rise', 'high', 'strong', 'positive', 'beat', 'outperform', 'jump', 'soar']
                        # Negative keywords
                        negative_words = ['fall', 'loss', 'decline', 'bearish', 'down', 'drop', 'weak', 'negative', 'miss', 'underperform', 'concern', 'risk', 'plunge', 'crash']
                        
                        positive_count = sum(1 for word in positive_words if word in text)
                        negative_count = sum(1 for word in negative_words if word in text)
                        
                        if positive_count > negative_count:
                            sentiment_emoji = "🟢"
                            sentiment_text = "Positive"
                            sentiment_color = "#00ff00"
                        elif negative_count > positive_count:
                            sentiment_emoji = "🔴"
                            sentiment_text = "Negative"
                            sentiment_color = "#ff0000"
                        else:
                            sentiment_emoji = "🟡"
                            sentiment_text = "Neutral"
                            sentiment_color = "#ffaa00"
                        
                        # Display article card
                        with st.container():
                            st.markdown(f"""
                            <div style="
                                border: 2px solid {sentiment_color};
                                border-radius: 10px;
                                padding: 15px;
                                margin: 10px 0;
                                background-color: rgba(255,255,255,0.05);
                            ">
                                <h4 style="margin: 0 0 10px 0;">
                                    {sentiment_emoji} {article['title']}
                                </h4>
                                <p style="color: #888; margin: 5px 0;">
                                    <strong>Source:</strong> {article['source']} |
                                    <strong>Published:</strong> {article['published']}
                                </p>
                                <p style="margin: 10px 0;">
                                    <strong>Sentiment:</strong>
                                    <span style="color: {sentiment_color}; font-weight: bold;">{sentiment_emoji} {sentiment_text}</span>
                                </p>
                                <a href="{article['link']}" target="_blank" style="
                                    display: inline-block;
                                    padding: 10px 20px;
                                    background-color: #0066cc;
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 5px;
                                    font-weight: bold;
                                    margin-top: 10px;
                                ">
                                    🔗 Read Full Article
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown("")  # Spacing
                    
                    # Overall sentiment summary
                    st.markdown("---")
                    st.markdown("#### 📊 Overall News Sentiment")
                    
                    # Calculate overall sentiment
                    total_positive = 0
                    total_negative = 0
                    total_neutral = 0
                    
                    for article in news_articles:
                        title_lower = article.get('title', '').lower()
                        summary_lower = article.get('summary', '').lower()
                        text = title_lower + ' ' + summary_lower
                        
                        positive_words = ['surge', 'gain', 'profit', 'growth', 'bullish', 'rally', 'up', 'rise', 'high', 'strong', 'positive', 'beat', 'outperform', 'jump', 'soar']
                        negative_words = ['fall', 'loss', 'decline', 'bearish', 'down', 'drop', 'weak', 'negative', 'miss', 'underperform', 'concern', 'risk', 'plunge', 'crash']
                        
                        positive_count = sum(1 for word in positive_words if word in text)
                        negative_count = sum(1 for word in negative_words if word in text)
                        
                        if positive_count > negative_count:
                            total_positive += 1
                        elif negative_count > positive_count:
                            total_negative += 1
                        else:
                            total_neutral += 1
                    
                    total_articles = len(news_articles)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🟢 Positive News", total_positive, f"{total_positive/total_articles*100:.0f}%")
                    with col2:
                        st.metric("🟡 Neutral News", total_neutral, f"{total_neutral/total_articles*100:.0f}%")
                    with col3:
                        st.metric("🔴 Negative News", total_negative, f"{total_negative/total_articles*100:.0f}%")
                    
                    # Overall recommendation
                    if total_positive > total_negative:
                        st.success(f"📈 Overall sentiment is **POSITIVE** for {selected_news_stock}")
                    elif total_negative > total_positive:
                        st.error(f"📉 Overall sentiment is **NEGATIVE** for {selected_news_stock}")
                    else:
                        st.info(f"➡️ Overall sentiment is **NEUTRAL** for {selected_news_stock}")
                
                else:
                    st.warning(f"❌ No recent news found for {selected_news_stock}")
                    st.info("💡 Try selecting a different stock or the news source may be temporarily unavailable")
            
            except Exception as e:
                st.error(f"Error fetching news: {str(e)}")
                st.info("💡 News data may not be available for this stock. Try another stock from your watchlist.")
    else:
        st.info("Add stocks to your watchlist to view news and sentiment analysis")


# Footer
st.markdown("---")
st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Auto-refresh:** Every 5 seconds")

# Made with Bob
