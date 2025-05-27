"""WebSocket endpoint for real-time MCP communication."""
import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlmodel import Session
from app.api.deps import get_db
from app.models import User
from app.services.mcp_manager import mcp_manager
from app.core.security import decode_token
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        
    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_json(message)
            
    async def broadcast(self, message: dict):
        for websocket in self.active_connections.values():
            await websocket.send_json(message)


manager = ConnectionManager()


async def get_current_user_from_token(token: str, session: Session) -> User:
    """Get current user from JWT token."""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token")
            
        user = session.get(User, user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
            
        return user
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    session: Session = Depends(get_db),
):
    """WebSocket endpoint for real-time MCP communication."""
    user = None
    try:
        # Authenticate user
        user = await get_current_user_from_token(token, session)
        await manager.connect(websocket, str(user.id))
        
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": str(user.id)
        })
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_json()
                await handle_websocket_message(websocket, user, data, session)
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON"
                })
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
    finally:
        if user:
            manager.disconnect(str(user.id))


async def handle_websocket_message(
    websocket: WebSocket,
    user: User,
    data: Dict[str, Any],
    session: Session
):
    """Handle incoming WebSocket messages."""
    msg_type = data.get("type")
    
    if msg_type == "ping":
        await websocket.send_json({"type": "pong"})
        
    elif msg_type == "tool_call":
        # Call tool on MCP server
        server_name = data.get("server")
        tool_name = data.get("tool")
        arguments = data.get("arguments", {})
        
        try:
            result = await mcp_manager.call_tool(server_name, tool_name, arguments)
            await websocket.send_json({
                "type": "tool_result",
                "server": server_name,
                "tool": tool_name,
                "result": result
            })
        except Exception as e:
            await websocket.send_json({
                "type": "tool_error",
                "server": server_name,
                "tool": tool_name,
                "error": str(e)
            })
            
    elif msg_type == "resource_get":
        # Get resource from MCP server
        server_name = data.get("server")
        uri = data.get("uri")
        
        try:
            result = await mcp_manager.get_resource(server_name, uri)
            await websocket.send_json({
                "type": "resource_result",
                "server": server_name,
                "uri": uri,
                "result": result
            })
        except Exception as e:
            await websocket.send_json({
                "type": "resource_error",
                "server": server_name,
                "uri": uri,
                "error": str(e)
            })
            
    elif msg_type == "prompt_get":
        # Get prompt from MCP server
        server_name = data.get("server")
        prompt_name = data.get("prompt")
        arguments = data.get("arguments", {})
        
        try:
            result = await mcp_manager.get_prompt(server_name, prompt_name, arguments)
            await websocket.send_json({
                "type": "prompt_result",
                "server": server_name,
                "prompt": prompt_name,
                "result": result
            })
        except Exception as e:
            await websocket.send_json({
                "type": "prompt_error",
                "server": server_name,
                "prompt": prompt_name,
                "error": str(e)
            })
            
    elif msg_type == "server_status":
        # Get status of all servers
        from app.models import MCPServer
        from sqlmodel import select
        
        servers = session.exec(select(MCPServer)).all()
        status_list = []
        
        for server in servers:
            status = {
                "id": str(server.id),
                "name": server.name,
                "status": "disconnected",
                "capabilities": None,
                "tools": None,
                "resources": None,
                "prompts": None
            }
            
            if server.name in mcp_manager.connections:
                connection = mcp_manager.connections[server.name]
                status["status"] = connection.server.status.value
                status["capabilities"] = connection.server.capabilities
                status["tools"] = connection.server.tools
                status["resources"] = connection.server.resources
                status["prompts"] = connection.server.prompts
                
            status_list.append(status)
            
        await websocket.send_json({
            "type": "server_status_result",
            "servers": status_list
        })
        
    else:
        await websocket.send_json({
            "type": "error",
            "error": f"Unknown message type: {msg_type}"
        })