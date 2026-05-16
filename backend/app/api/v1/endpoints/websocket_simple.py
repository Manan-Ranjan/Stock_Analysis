"""
Simplified WebSocket endpoint without Redis dependency
Real-time stock data streaming
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import asyncio
import json
import logging
from datetime import datetime
import yfinance as yf

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active connections
active_connections: Set[WebSocket] = set()

# Default watchlist
DEFAULT_WATCHLIST = ['HDFCBANK.NS', 'RELIANCE.NS', 'INFY.NS', 'TCS.NS', 'ICICIBANK.NS']


async def get_stock_data(symbol: str) -> dict:
    """Fetch current stock data"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        
        if not data.empty:
            latest = data.iloc[-1]
            return {
                'symbol': symbol.replace('.NS', ''),
                'price': float(latest['Close']),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
    
    return None


async def broadcast_stock_updates():
    """Broadcast stock updates to all connected clients"""
    while True:
        try:
            if active_connections:
                # Fetch data for all stocks in watchlist
                updates = []
                for symbol in DEFAULT_WATCHLIST:
                    data = await get_stock_data(symbol)
                    if data:
                        updates.append(data)
                
                if updates:
                    message = json.dumps({
                        'type': 'stock_update',
                        'data': updates,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Send to all connected clients
                    disconnected = set()
                    for connection in active_connections:
                        try:
                            await connection.send_text(message)
                        except:
                            disconnected.add(connection)
                    
                    # Remove disconnected clients
                    active_connections.difference_update(disconnected)
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error in broadcast: {e}")
            await asyncio.sleep(5)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time stock updates
    """
    await websocket.accept()
    active_connections.add(websocket)
    
    logger.info(f"Client connected. Total connections: {len(active_connections)}")
    
    # Send welcome message
    await websocket.send_json({
        'type': 'connection',
        'status': 'connected',
        'message': 'Connected to Real-Time Stock Analysis Platform',
        'watchlist': [s.replace('.NS', '') for s in DEFAULT_WATCHLIST],
        'timestamp': datetime.now().isoformat()
    })
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get('type') == 'ping':
                    await websocket.send_json({
                        'type': 'pong',
                        'timestamp': datetime.now().isoformat()
                    })
                
                elif message.get('type') == 'subscribe':
                    # Handle subscription to specific stocks
                    symbols = message.get('symbols', [])
                    await websocket.send_json({
                        'type': 'subscribed',
                        'symbols': symbols,
                        'timestamp': datetime.now().isoformat()
                    })
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                })
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                
    except WebSocketDisconnect:
        pass
    finally:
        active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(active_connections)}")


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        'active_connections': len(active_connections),
        'watchlist': [s.replace('.NS', '') for s in DEFAULT_WATCHLIST],
        'status': 'active' if active_connections else 'idle',
        'timestamp': datetime.now().isoformat()
    }


# Start background task for broadcasting
@router.on_event("startup")
async def start_broadcast():
    """Start the broadcast task"""
    asyncio.create_task(broadcast_stock_updates())
    logger.info("WebSocket broadcast task started")


# Made with Bob