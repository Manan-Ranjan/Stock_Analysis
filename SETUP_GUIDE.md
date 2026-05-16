# Real-Time Stock Analysis Platform - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Docker and Docker Compose (recommended)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)

---

## Option 1: Docker Setup (Recommended)

### 1. Clone and Setup
```bash
cd /Users/mananranjan/Desktop/Hackathon/StockAnalysis

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional)
nano .env
```

### 2. Start All Services
```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Access the Application
- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/api/v1/ws
- **Celery Flower**: http://localhost:5555

### 4. Stop Services
```bash
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## Option 2: Local Development Setup

### 1. Install Dependencies

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup Database

#### PostgreSQL
```bash
# Install PostgreSQL
brew install postgresql@15  # macOS
# or
sudo apt-get install postgresql-15  # Ubuntu

# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb stockanalysis
createuser stockuser -P  # Enter password: stockpass
```

#### Redis
```bash
# Install Redis
brew install redis  # macOS
# or
sudo apt-get install redis-server  # Ubuntu

# Start Redis
brew services start redis
# or
sudo systemctl start redis
```

### 3. Configure Environment
```bash
# Copy and edit .env
cp .env.example .env

# Update database URLs
DATABASE_URL=postgresql://stockuser:stockpass@localhost:5432/stockanalysis
REDIS_URL=redis://localhost:6379/0
```

### 4. Run Backend
```bash
cd backend

# Initialize database
python -c "from app.core.database import init_db; init_db()"

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.core.celery_app worker --loglevel=info

# In another terminal, start Celery beat
celery -A app.core.celery_app beat --loglevel=info
```

### 5. Run Frontend
```bash
cd frontend
streamlit run Home.py --server.port 8501
```

---

## 🧪 Testing the Setup

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app_name": "Real-Time Stock Analysis Platform",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Test WebSocket Connection

#### Using Python
```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/ws"
    
    async with websockets.connect(uri) as websocket:
        # Subscribe to stocks
        await websocket.send(json.dumps({
            "action": "subscribe",
            "symbols": ["HDFCBANK", "RELIANCE"]
        }))
        
        # Receive messages
        for i in range(5):
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.run(test_websocket())
```

#### Using JavaScript (Browser Console)
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws');

ws.onopen = () => {
    console.log('Connected');
    ws.send(JSON.stringify({
        action: 'subscribe',
        symbols: ['HDFCBANK', 'RELIANCE']
    }));
};

ws.onmessage = (event) => {
    console.log('Received:', JSON.parse(event.data));
};
```

### 3. Test API Endpoints
```bash
# Get WebSocket stats
curl http://localhost:8000/api/v1/ws/stats

# Access API documentation
open http://localhost:8000/docs
```

---

## 📊 Using the Platform

### 1. Real-Time Stock Monitoring

#### Via Streamlit UI
1. Open http://localhost:8501
2. Navigate to "Live Dashboard"
3. Add stocks to watchlist
4. View real-time price updates

#### Via WebSocket
```python
import asyncio
import websockets
import json

async def monitor_stocks():
    uri = "ws://localhost:8000/api/v1/ws?client_id=my_client"
    
    async with websockets.connect(uri) as ws:
        # Subscribe to multiple stocks
        await ws.send(json.dumps({
            "action": "subscribe",
            "symbols": ["HDFCBANK", "ICICIBANK", "RELIANCE", "TCS"]
        }))
        
        # Listen for updates
        while True:
            message = await ws.recv()
            data = json.loads(message)
            
            if data["type"] == "price_update":
                print(f"{data['symbol']}: ₹{data['data']['price']}")
            elif data["type"] == "signal":
                print(f"🎯 Signal for {data['symbol']}: {data['data']}")

asyncio.run(monitor_stocks())
```

### 2. Analyze Stocks
```python
# Using your existing momentum trading system
from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators

fetcher = DataFetcher()
data = fetcher.fetch_stock_data('HDFCBANK', days=90)
data = MomentumIndicators.add_all_momentum_indicators(data)

print(data.tail())
```

### 3. Paper Trading
```python
# Via API (coming soon)
import requests

response = requests.post('http://localhost:8000/api/v1/paper-trading/order', json={
    "symbol": "HDFCBANK",
    "action": "BUY",
    "quantity": 10,
    "order_type": "MARKET"
})
```

---

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Enable/Disable Features
ENABLE_REAL_TIME_STREAMING=True
ENABLE_PREDICTIONS=True
ENABLE_PAPER_TRADING=True

# Data Update Intervals
PRICE_UPDATE_INTERVAL=5  # seconds
MARKET_DATA_CACHE_TTL=60  # seconds

# WebSocket Settings
WS_MAX_CONNECTIONS=1000
WS_HEARTBEAT_INTERVAL=30

# External APIs (optional)
FINNHUB_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

### Customizing Stock List

Edit `stocks_config.csv`:
```csv
symbol,sector,exchange
HDFCBANK,Banking,NSE
RELIANCE,Energy,NSE
INFY,IT,NSE
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if ports are in use
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Check logs
docker-compose logs backend
```

### WebSocket connection fails
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check WebSocket stats
curl http://localhost:8000/api/v1/ws/stats

# Test with wscat
npm install -g wscat
wscat -c ws://localhost:8000/api/v1/ws
```

### Database connection error
```bash
# Check PostgreSQL is running
docker-compose ps postgres
# or
pg_isready -h localhost -p 5432

# Check credentials in .env
cat .env | grep DATABASE_URL
```

### Redis connection error
```bash
# Check Redis is running
docker-compose ps redis
# or
redis-cli ping

# Should return: PONG
```

---

## 📈 Performance Tuning

### For High-Frequency Updates
```bash
# In .env
PRICE_UPDATE_INTERVAL=1  # Update every second
REDIS_MAX_CONNECTIONS=100
WS_MAX_CONNECTIONS=5000
```

### For Large Portfolios
```bash
# Increase database pool
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20

# Increase cache TTL
MARKET_DATA_CACHE_TTL=300
```

---

## 🔐 Security (Production)

### 1. Change Secret Keys
```bash
# Generate new secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update in .env
SECRET_KEY=your_new_secret_key_here
```

### 2. Enable HTTPS
```bash
# Use nginx reverse proxy
# See nginx/nginx.conf for configuration
```

### 3. Restrict CORS
```bash
# In .env
CORS_ORIGINS=["https://yourdomain.com"]
```

---

## 📚 Next Steps

1. ✅ Setup complete - Platform is running
2. 📊 Explore the Streamlit dashboard
3. 🔌 Test WebSocket connections
4. 📈 Add your favorite stocks to watchlist
5. 🤖 Enable predictive analytics
6. 📱 Try paper trading
7. 🚀 Deploy to production

---

## 🆘 Getting Help

- Check logs: `docker-compose logs -f`
- API docs: http://localhost:8000/docs
- GitHub Issues: [Create an issue]
- Documentation: See `REALTIME_PLATFORM_ARCHITECTURE.md`

---

**Platform Status**: ✅ Ready for Development
**Last Updated**: 2026-05-16