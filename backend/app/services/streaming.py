"""
Real-Time Streaming Service
Manages WebSocket connections and broadcasts live market data
"""

import asyncio
import json
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import logging

from app.core.database import get_redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Active connections: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Subscriptions: {symbol: Set[client_id]}
        self.subscriptions: Dict[str, Set[str]] = {}
        
        # Client metadata: {client_id: {user_id, watchlist, etc}}
        self.client_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Message queue for each client
        self.message_queues: Dict[str, asyncio.Queue] = {}
        
        # Heartbeat tasks
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, user_id: Optional[str] = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        self.active_connections[client_id] = websocket
        self.message_queues[client_id] = asyncio.Queue(maxsize=settings.WS_MESSAGE_QUEUE_SIZE)
        self.client_metadata[client_id] = {
            "user_id": user_id,
            "connected_at": datetime.now().isoformat(),
            "subscriptions": []
        }
        
        # Start heartbeat
        self.heartbeat_tasks[client_id] = asyncio.create_task(
            self._heartbeat(client_id)
        )
        
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }, client_id)
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            # Cancel heartbeat
            if client_id in self.heartbeat_tasks:
                self.heartbeat_tasks[client_id].cancel()
                del self.heartbeat_tasks[client_id]
            
            # Remove from all subscriptions
            for symbol in list(self.subscriptions.keys()):
                if client_id in self.subscriptions[symbol]:
                    self.subscriptions[symbol].remove(client_id)
                    if not self.subscriptions[symbol]:
                        del self.subscriptions[symbol]
            
            # Clean up
            del self.active_connections[client_id]
            if client_id in self.message_queues:
                del self.message_queues[client_id]
            if client_id in self.client_metadata:
                del self.client_metadata[client_id]
            
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe(self, client_id: str, symbols: list):
        """Subscribe client to stock symbols"""
        for symbol in symbols:
            if symbol not in self.subscriptions:
                self.subscriptions[symbol] = set()
            self.subscriptions[symbol].add(client_id)
            
            if client_id in self.client_metadata:
                if symbol not in self.client_metadata[client_id]["subscriptions"]:
                    self.client_metadata[client_id]["subscriptions"].append(symbol)
        
        logger.info(f"Client {client_id} subscribed to {symbols}")
        
        await self.send_personal_message({
            "type": "subscription",
            "status": "subscribed",
            "symbols": symbols,
            "timestamp": datetime.now().isoformat()
        }, client_id)
    
    async def unsubscribe(self, client_id: str, symbols: list):
        """Unsubscribe client from stock symbols"""
        for symbol in symbols:
            if symbol in self.subscriptions and client_id in self.subscriptions[symbol]:
                self.subscriptions[symbol].remove(client_id)
                if not self.subscriptions[symbol]:
                    del self.subscriptions[symbol]
                
                if client_id in self.client_metadata:
                    if symbol in self.client_metadata[client_id]["subscriptions"]:
                        self.client_metadata[client_id]["subscriptions"].remove(symbol)
        
        logger.info(f"Client {client_id} unsubscribed from {symbols}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_symbol(self, symbol: str, message: dict):
        """Broadcast message to all clients subscribed to a symbol"""
        if symbol in self.subscriptions:
            disconnected_clients = []
            
            for client_id in self.subscriptions[symbol]:
                try:
                    await self.send_personal_message(message, client_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)
            
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                self.disconnect(client_id)
    
    async def broadcast_all(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        
        for client_id in list(self.active_connections.keys()):
            try:
                await self.send_personal_message(message, client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def _heartbeat(self, client_id: str):
        """Send periodic heartbeat to keep connection alive"""
        while client_id in self.active_connections:
            try:
                await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
                await self.send_personal_message({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error for {client_id}: {e}")
                break
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": sum(len(clients) for clients in self.subscriptions.values()),
            "unique_symbols": len(self.subscriptions),
            "symbols": list(self.subscriptions.keys())
        }


# Global connection manager instance
manager = ConnectionManager()


class MarketDataStreamer:
    """Streams real-time market data to connected clients"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.is_streaming = False
        self.stream_task: Optional[asyncio.Task] = None
    
    async def start_streaming(self):
        """Start streaming market data"""
        if self.is_streaming:
            logger.warning("Streaming already active")
            return
        
        self.is_streaming = True
        self.stream_task = asyncio.create_task(self._stream_loop())
        logger.info("Market data streaming started")
    
    async def stop_streaming(self):
        """Stop streaming market data"""
        self.is_streaming = False
        if self.stream_task:
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
        logger.info("Market data streaming stopped")
    
    async def _stream_loop(self):
        """Main streaming loop"""
        redis = await get_redis()
        
        while self.is_streaming:
            try:
                # Get all subscribed symbols
                symbols = list(self.manager.subscriptions.keys())
                
                if not symbols:
                    await asyncio.sleep(1)
                    continue
                
                # Fetch latest data for subscribed symbols
                for symbol in symbols:
                    try:
                        # Check Redis cache first
                        cached_data = await redis.get(f"price:{symbol}")
                        
                        if cached_data:
                            price_data = json.loads(cached_data)
                            
                            # Broadcast to subscribers
                            await self.manager.broadcast_to_symbol(symbol, {
                                "type": "price_update",
                                "symbol": symbol,
                                "data": price_data,
                                "timestamp": datetime.now().isoformat()
                            })
                    
                    except Exception as e:
                        logger.error(f"Error streaming {symbol}: {e}")
                
                # Wait before next update
                await asyncio.sleep(settings.PRICE_UPDATE_INTERVAL)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Streaming loop error: {e}")
                await asyncio.sleep(5)
    
    async def publish_price_update(self, symbol: str, price_data: dict):
        """Publish price update to Redis and broadcast to clients"""
        try:
            redis = await get_redis()
            
            # Cache in Redis
            await redis.setex(
                f"price:{symbol}",
                settings.MARKET_DATA_CACHE_TTL,
                json.dumps(price_data)
            )
            
            # Broadcast to subscribers
            await self.manager.broadcast_to_symbol(symbol, {
                "type": "price_update",
                "symbol": symbol,
                "data": price_data,
                "timestamp": datetime.now().isoformat()
            })
        
        except Exception as e:
            logger.error(f"Error publishing price update for {symbol}: {e}")
    
    async def publish_signal(self, symbol: str, signal_data: dict):
        """Publish trading signal to subscribers"""
        try:
            await self.manager.broadcast_to_symbol(symbol, {
                "type": "signal",
                "symbol": symbol,
                "data": signal_data,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error publishing signal for {symbol}: {e}")
    
    async def publish_alert(self, client_id: str, alert_data: dict):
        """Send alert to specific client"""
        try:
            await self.manager.send_personal_message({
                "type": "alert",
                "data": alert_data,
                "timestamp": datetime.now().isoformat()
            }, client_id)
        except Exception as e:
            logger.error(f"Error publishing alert to {client_id}: {e}")


# Global streamer instance
streamer = MarketDataStreamer(manager)

# Made with Bob
