"""MCP Server model for storing server configurations."""
import enum
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from app.models.base import BaseDBModel


class MCPTransportType(str, enum.Enum):
    """MCP transport protocol types."""
    STDIO = "stdio"
    HTTP_SSE = "http_sse"


class MCPServerStatus(str, enum.Enum):
    """MCP server connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class MCPServerBase(SQLModel):
    """Base MCP server configuration."""
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    transport: MCPTransportType = Field(default=MCPTransportType.STDIO)
    command: Optional[str] = Field(default=None, description="Command to execute for stdio transport")
    args: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    url: Optional[str] = Field(default=None, description="URL for HTTP+SSE transport")
    headers: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    is_enabled: bool = Field(default=True)
    is_remote: bool = Field(default=False)
    auth_type: Optional[str] = Field(default=None, description="Authentication type: 'api_key', 'bearer', 'basic'")
    auth_config: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON), description="Authentication configuration")


class MCPServer(BaseDBModel, MCPServerBase, table=True):
    """MCP server configuration stored in database."""
    __tablename__ = "mcp_servers"
    
    # Server capabilities (discovered after connection)
    capabilities: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tools: Optional[list[dict]] = Field(default=None, sa_column=Column(JSON))
    resources: Optional[list[dict]] = Field(default=None, sa_column=Column(JSON))
    prompts: Optional[list[dict]] = Field(default=None, sa_column=Column(JSON))


class MCPServerCreate(MCPServerBase):
    """Schema for creating MCP server."""
    pass


class MCPServerUpdate(SQLModel):
    """Schema for updating MCP server."""
    name: Optional[str] = None
    description: Optional[str] = None
    transport: Optional[MCPTransportType] = None
    command: Optional[str] = None
    args: Optional[list[str]] = None
    url: Optional[str] = None
    headers: Optional[dict[str, str]] = None
    is_enabled: Optional[bool] = None
    is_remote: Optional[bool] = None
    auth_type: Optional[str] = None
    auth_config: Optional[dict[str, str]] = None


class MCPServerPublic(MCPServerBase):
    """Public schema for MCP server."""
    id: UUID
    status: MCPServerStatus = MCPServerStatus.DISCONNECTED
    error_message: Optional[str] = None
    capabilities: Optional[dict] = None
    tools: Optional[list[dict]] = None
    resources: Optional[list[dict]] = None
    prompts: Optional[list[dict]] = None
    created_at: datetime
    updated_at: datetime