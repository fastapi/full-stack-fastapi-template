"""API routes for MCP server management."""
from typing import List, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.api.deps import get_current_active_user, get_current_active_superuser, get_db
from app.models import User
from app.models.mcp_server import (
    MCPServer, 
    MCPServerStatus, 
    MCPServerBase, 
    MCPServerCreate, 
    MCPServerUpdate, 
    MCPServerPublic
)
from app.services.mcp_manager import mcp_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/servers", response_model=List[MCPServerPublic])
async def list_mcp_servers(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[MCPServerPublic]:
    """List all MCP servers."""
    servers = session.execute(select(MCPServer)).scalars().all()
    
    # Update runtime data from manager
    result = []
    for server in servers:
        server_dict = server.model_dump()
        if server.name in mcp_manager.connections:
            connection = mcp_manager.connections[server.name]
            server_dict["status"] = connection.status
            server_dict["error_message"] = connection.error_message
        else:
            server_dict["status"] = MCPServerStatus.DISCONNECTED
            server_dict["error_message"] = None
        result.append(MCPServerPublic(**server_dict))
    
    return result


@router.post("/servers", response_model=MCPServerPublic)
async def create_mcp_server(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    server_in: MCPServerCreate,
) -> MCPServerPublic:
    """Create a new MCP server configuration."""
    # Check if server with same name exists
    existing = session.execute(select(MCPServer).where(MCPServer.name == server_in.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Server with this name already exists")
    
    server = MCPServer.model_validate(server_in)
    session.add(server)
    session.commit()
    session.refresh(server)
    
    # Auto-connect if enabled
    if server.is_enabled:
        try:
            await mcp_manager.connect_server(server)
        except Exception as e:
            logger.error(f"Failed to connect to server {server.name}: {e}")
    
    return server


@router.get("/servers/{server_id}", response_model=MCPServerPublic)
async def get_mcp_server(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    server_id: str,
) -> MCPServerPublic:
    """Get MCP server by ID."""
    server = session.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Update runtime data from manager
    server_dict = server.model_dump()
    if server.name in mcp_manager.connections:
        connection = mcp_manager.connections[server.name]
        server_dict["status"] = connection.status
        server_dict["error_message"] = connection.error_message
    else:
        server_dict["status"] = MCPServerStatus.DISCONNECTED
        server_dict["error_message"] = None
    
    return MCPServerPublic(**server_dict)


@router.patch("/servers/{server_id}", response_model=MCPServerPublic)
async def update_mcp_server(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    server_id: str,
    server_in: MCPServerUpdate,
) -> MCPServerPublic:
    """Update MCP server configuration."""
    server = session.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Disconnect if connected
    if server.name in mcp_manager.connections:
        await mcp_manager.disconnect_server(server.name)
    
    # Update server
    update_data = server_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(server, key, value)
    
    session.add(server)
    session.commit()
    session.refresh(server)
    
    # Reconnect if enabled
    if server.is_enabled:
        try:
            await mcp_manager.connect_server(server)
        except Exception as e:
            logger.error(f"Failed to connect to server {server.name}: {e}")
    
    return server


@router.delete("/servers/{server_id}")
async def delete_mcp_server(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    server_id: str,
) -> dict:
    """Delete MCP server."""
    server = session.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Disconnect if connected
    if server.name in mcp_manager.connections:
        await mcp_manager.disconnect_server(server.name)
    
    session.delete(server)
    session.commit()
    
    return {"message": "Server deleted successfully"}


@router.post("/servers/{server_id}/connect")
async def connect_mcp_server(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    server_id: str,
) -> dict:
    """Connect to an MCP server."""
    server = session.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if not server.is_enabled:
        raise HTTPException(status_code=400, detail="Server is disabled")
    
    try:
        success = await mcp_manager.connect_server(server)
        if success:
            # Update server with discovered capabilities
            session.add(server)
            session.commit()
            return {"message": "Connected successfully", "status": mcp_manager.connections[server.name].status.value}
        else:
            connection = mcp_manager.connections.get(server.name)
            error_msg = connection.error_message if connection else "Failed to connect"
            raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/{server_id}/disconnect")
async def disconnect_mcp_server(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    server_id: str,
) -> dict:
    """Disconnect from an MCP server."""
    server = session.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if server.name not in mcp_manager.connections:
        raise HTTPException(status_code=400, detail="Server not connected")
    
    await mcp_manager.disconnect_server(server.name)
    return {"message": "Disconnected successfully"}


@router.post("/servers/{server_id}/tools/{tool_name}/call")
async def call_mcp_tool(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    server_id: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> Any:
    """Call a tool on an MCP server."""
    server = session.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if server.name not in mcp_manager.connections:
        raise HTTPException(status_code=400, detail="Server not connected")
    
    try:
        result = await mcp_manager.call_tool(server.name, tool_name, arguments)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}/resources/{uri:path}")
async def get_mcp_resource(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    server_id: str,
    uri: str,
) -> Any:
    """Get a resource from an MCP server."""
    server = session.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if server.name not in mcp_manager.connections:
        raise HTTPException(status_code=400, detail="Server not connected")
    
    try:
        result = await mcp_manager.get_resource(server.name, uri)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/{server_id}/prompts/{prompt_name}")
async def get_mcp_prompt(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    server_id: str,
    prompt_name: str,
    arguments: dict[str, Any],
) -> Any:
    """Get a prompt from an MCP server."""
    server = session.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if server.name not in mcp_manager.connections:
        raise HTTPException(status_code=400, detail="Server not connected")
    
    try:
        result = await mcp_manager.get_prompt(server.name, prompt_name, arguments)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))