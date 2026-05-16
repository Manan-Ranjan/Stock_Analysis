"""
WebSocket endpoints for real-time data streaming
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
import json
import uuid

from app.services.streaming import manager, streamer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time market data streaming
    
    Usage:
        ws://localhost:8000/api/v1/ws?client_id=abc123&user_id=user1
    
    Message Format:
        Client -> Server:
        {
            "action": "subscribe" | "unsubscribe" | "ping",
            "symbols": ["HDFCBANK", "RELIANCE"],
            "data": {}
        }
        
        Server -> Client:
        {
            "type": "price_update" | "signal" | "alert" | "heartbeat",
            "symbol": "HDFCBANK",
            "data": {...},
            "timestamp": "2024-01-01T12:00:00"
        }
    """
    
    # Generate client ID if not provided
    if not client_id:
        client_id = str(uuid.uuid4())
    
    # Connect client
    await manager.connect(websocket, client_id, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "subscribe":
                    # Subscribe to symbols
                    symbols = message.get("symbols", [])
                    if symbols:
                        await manager.subscribe(client_id, symbols)
                        logger.info(f"Client {client_id} subscribed to {symbols}")
                
                elif action == "unsubscribe":
                    # Unsubscribe from symbols
                    symbols = message.get("symbols", [])
                    if symbols:
                        await manager.unsubscribe(client_id, symbols)
                        logger.info(f"Client {client_id} unsubscribed from {symbols}")
                
                elif action == "ping":
                    # Respond to ping
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }, client_id)
                
                elif action == "get_stats":
                    # Send connection statistics
                    stats = manager.get_stats()
                    await manager.send_personal_message({
                        "type": "stats",
                        "data": stats
                    }, client_id)
                
                else:
                    # Unknown action
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    }, client_id)
            
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, client_id)
            
            except Exception as e:
                logger.error(f"Error processing message from {client_id}: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e)
                }, client_id)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return manager.get_stats()


@router.post("/ws/broadcast")
async def broadcast_message(message: dict):
    """
    Broadcast message to all connected clients
    (Admin endpoint - should be protected)
    """
    await manager.broadcast_all(message)
    return {"status": "broadcasted", "connections": len(manager.active_connections)}


@router.post("/ws/publish/{symbol}")
async def publish_price_update(symbol: str, price_data: dict):
    """
    Publish price update for a symbol
    (Internal endpoint - should be protected)
    """
    await streamer.publish_price_update(symbol, price_data)
    return {"status": "published", "symbol": symbol}

# Made with Bob
