"""MCP Server Manager for handling MCP server connections."""
import asyncio
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import subprocess
import aiohttp
from app.models.mcp_server import MCPServer, MCPServerStatus, MCPTransportType
from app.core.config import settings

logger = logging.getLogger(__name__)


class MCPConnection:
    """Represents a connection to an MCP server."""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.process: Optional[subprocess.Popen] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._read_task: Optional[asyncio.Task] = None
        self._message_id = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}
        # Runtime status
        self.status: MCPServerStatus = MCPServerStatus.DISCONNECTED
        self.error_message: Optional[str] = None
        
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            if self.server.transport == MCPTransportType.STDIO:
                return await self._connect_stdio()
            elif self.server.transport == MCPTransportType.HTTP_SSE:
                return await self._connect_http_sse()
            else:
                raise ValueError(f"Unsupported transport: {self.server.transport}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.server.name}: {e}")
            self.status = MCPServerStatus.ERROR
            self.error_message = str(e)
            return False
            
    async def _connect_stdio(self) -> bool:
        """Connect to MCP server via stdio."""
        if not self.server.command:
            raise ValueError("Command is required for stdio transport")
            
        args = [self.server.command]
        if self.server.args:
            args.extend(self.server.args)
            
        # Start the process
        self.process = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        self.reader = self.process.stdout
        self.writer = self.process.stdin
        
        # Start reading messages
        self._read_task = asyncio.create_task(self._read_messages())
        
        # Send initialize request
        response = await self._send_request("initialize", {
            "protocolVersion": "0.1.0",
            "capabilities": {
                "roots": True,
                "tools": True,
                "prompts": True,
                "resources": True
            },
            "clientInfo": {
                "name": "copilot-mcp-host",
                "version": "0.1.0"
            }
        })
        
        if response and "capabilities" in response:
            self.server.capabilities = response["capabilities"]
            self.status = MCPServerStatus.CONNECTED
            
            # Fetch available tools, resources, and prompts
            await self._fetch_server_features()
            return True
            
        return False
        
    async def _connect_http_sse(self) -> bool:
        """Connect to MCP server via HTTP+SSE."""
        if not self.server.url:
            raise ValueError("URL is required for HTTP+SSE transport")
            
        self.session = aiohttp.ClientSession(headers=self.server.headers or {})
        
        # Send initialize request
        response = await self._send_http_request("initialize", {
            "protocolVersion": "0.1.0",
            "capabilities": {
                "roots": True,
                "tools": True,
                "prompts": True,
                "resources": True
            },
            "clientInfo": {
                "name": "copilot-mcp-host",
                "version": "0.1.0"
            }
        })
        
        if response and "capabilities" in response:
            self.server.capabilities = response["capabilities"]
            self.status = MCPServerStatus.CONNECTED
            
            # Fetch available tools, resources, and prompts
            await self._fetch_server_features()
            return True
            
        return False
        
    async def _fetch_server_features(self):
        """Fetch available tools, resources, and prompts from the server."""
        # Fetch tools
        if self.server.capabilities.get("tools"):
            tools_response = await self._send_request("tools/list", {})
            if tools_response and "tools" in tools_response:
                self.server.tools = tools_response["tools"]
                
        # Fetch resources
        if self.server.capabilities.get("resources"):
            resources_response = await self._send_request("resources/list", {})
            if resources_response and "resources" in resources_response:
                self.server.resources = resources_response["resources"]
                
        # Fetch prompts
        if self.server.capabilities.get("prompts"):
            prompts_response = await self._send_request("prompts/list", {})
            if prompts_response and "prompts" in prompts_response:
                self.server.prompts = prompts_response["prompts"]
    
    async def _send_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC request to the server."""
        if self.server.transport == MCPTransportType.STDIO:
            return await self._send_stdio_request(method, params)
        elif self.server.transport == MCPTransportType.HTTP_SSE:
            return await self._send_http_request(method, params)
            
    async def _send_stdio_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a request via stdio."""
        if not self.writer:
            raise RuntimeError("Not connected")
            
        self._message_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self._message_id,
            "method": method,
            "params": params
        }
        
        # Create a future for this request
        future = asyncio.Future()
        self._pending_requests[self._message_id] = future
        
        # Send the message
        message_str = json.dumps(message) + "\n"
        self.writer.write(message_str.encode())
        await self.writer.drain()
        
        # Wait for response
        try:
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
        except asyncio.TimeoutError:
            self._pending_requests.pop(self._message_id, None)
            raise
            
    async def _send_http_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a request via HTTP."""
        if not self.session:
            raise RuntimeError("Not connected")
            
        self._message_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self._message_id,
            "method": method,
            "params": params
        }
        
        async with self.session.post(self.server.url, json=message) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise RuntimeError(f"HTTP error: {response.status}")
                
    async def _read_messages(self):
        """Read messages from stdio."""
        buffer = ""
        while self.reader and not self.reader.at_eof():
            try:
                data = await self.reader.read(1024)
                if not data:
                    break
                    
                buffer += data.decode()
                
                # Process complete messages
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            message = json.loads(line)
                            await self._handle_message(message)
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON: {line}")
                            
            except Exception as e:
                logger.error(f"Error reading messages: {e}")
                break
                
    async def _handle_message(self, message: Dict[str, Any]):
        """Handle an incoming message."""
        if "id" in message and message["id"] in self._pending_requests:
            # This is a response to our request
            future = self._pending_requests.pop(message["id"])
            if "result" in message:
                future.set_result(message["result"])
            elif "error" in message:
                future.set_exception(RuntimeError(message["error"]))
                
    async def disconnect(self):
        """Disconnect from the MCP server."""
        try:
            if self._read_task:
                self._read_task.cancel()
                
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
                
            if self.process:
                self.process.terminate()
                await self.process.wait()
                
            if self.session:
                await self.session.close()
                
            self.status = MCPServerStatus.DISCONNECTED
            
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {self.server.name}: {e}")
            
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        response = await self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        return response
        
    async def get_resource(self, uri: str) -> Any:
        """Get a resource from the MCP server."""
        response = await self._send_request("resources/read", {
            "uri": uri
        })
        return response
        
    async def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Get a prompt from the MCP server."""
        response = await self._send_request("prompts/get", {
            "name": name,
            "arguments": arguments
        })
        return response


class MCPServerManager:
    """Manager for MCP server connections."""
    
    def __init__(self):
        self.connections: Dict[str, MCPConnection] = {}
        
    async def connect_server(self, server: MCPServer) -> bool:
        """Connect to an MCP server."""
        if server.name in self.connections:
            await self.disconnect_server(server.name)
            
        # Set connecting status
        connection = MCPConnection(server)
        
        if await connection.connect():
            self.connections[server.name] = connection
            return True
        else:
            return False
            
    async def disconnect_server(self, server_name: str):
        """Disconnect from an MCP server."""
        if server_name in self.connections:
            connection = self.connections.pop(server_name)
            await connection.disconnect()
            
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific MCP server."""
        if server_name not in self.connections:
            raise RuntimeError(f"Server {server_name} not connected")
            
        return await self.connections[server_name].call_tool(tool_name, arguments)
        
    async def get_resource(self, server_name: str, uri: str) -> Any:
        """Get a resource from a specific MCP server."""
        if server_name not in self.connections:
            raise RuntimeError(f"Server {server_name} not connected")
            
        return await self.connections[server_name].get_resource(uri)
        
    async def get_prompt(self, server_name: str, name: str, arguments: Dict[str, Any]) -> Any:
        """Get a prompt from a specific MCP server."""
        if server_name not in self.connections:
            raise RuntimeError(f"Server {server_name} not connected")
            
        return await self.connections[server_name].get_prompt(name, arguments)
        
    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        for server_name in list(self.connections.keys()):
            await self.disconnect_server(server_name)


# Global instance
mcp_manager = MCPServerManager()