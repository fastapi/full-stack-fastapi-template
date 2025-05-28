"""MCP Server Manager for handling MCP server connections."""
import asyncio
import json
import logging
import os
import re
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
        
    def _expand_env_vars(self, value: str) -> str:
        """Expand environment variables in a string."""
        # Replace ${VAR} and $VAR patterns with environment variable values
        def replace_env_var(match):
            var_name = match.group(1) or match.group(2)
            return os.environ.get(var_name, match.group(0))
        
        # Match ${VAR} or $VAR patterns
        pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
        return re.sub(pattern, replace_env_var, value)
    
    def _expand_config_env_vars(self, config: Any) -> Any:
        """Recursively expand environment variables in configuration."""
        if isinstance(config, str):
            return self._expand_env_vars(config)
        elif isinstance(config, dict):
            return {k: self._expand_config_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._expand_config_env_vars(item) for item in config]
        return config
        
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
            
        # Expand environment variables in command and args
        command = self._expand_env_vars(self.server.command)
        args = [command]
        if self.server.args:
            expanded_args = [self._expand_env_vars(arg) for arg in self.server.args]
            args.extend(expanded_args)
            
        # Start the process
        try:
            self.process = await asyncio.create_subprocess_exec(
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ}  # Pass current environment variables
            )
        except FileNotFoundError:
            raise RuntimeError(f"Command not found: {command}")
        except Exception as e:
            raise RuntimeError(f"Failed to start process: {str(e)}")
        
        self.reader = self.process.stdout
        self.writer = self.process.stdin
        
        # Check if process started successfully
        await asyncio.sleep(0.1)  # Give process time to start
        if self.process.returncode is not None:
            stderr = await self.process.stderr.read()
            raise RuntimeError(f"Process exited immediately with code {self.process.returncode}: {stderr.decode()}")
        
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
            
        # Expand environment variables in URL
        url = self._expand_env_vars(self.server.url)
        
        # Build headers with authentication
        headers = self._expand_config_env_vars(dict(self.server.headers or {}))
        if self.server.auth_type and self.server.auth_config:
            # Expand environment variables in auth config
            auth_config = self._expand_config_env_vars(self.server.auth_config)
            
            if self.server.auth_type == "bearer":
                token = auth_config.get("token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            elif self.server.auth_type == "api_key":
                key_name = auth_config.get("key_name", "X-API-Key")
                api_key = auth_config.get("api_key")
                if api_key:
                    headers[key_name] = api_key
            elif self.server.auth_type == "basic":
                username = auth_config.get("username")
                password = auth_config.get("password")
                if username and password:
                    import base64
                    auth_str = f"{username}:{password}"
                    b64_auth = base64.b64encode(auth_str.encode()).decode()
                    headers["Authorization"] = f"Basic {b64_auth}"
        
        self.session = aiohttp.ClientSession(headers=headers)
        
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
        
        # Use the expanded URL
        url = self._expand_env_vars(self.server.url)
        
        try:
            async with self.session.post(url, json=message, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    result = await response.json()
                    if "error" in result:
                        raise RuntimeError(f"JSON-RPC error: {result['error']}")
                    return result.get("result")
                else:
                    text = await response.text()
                    raise RuntimeError(f"HTTP error {response.status}: {text}")
        except asyncio.TimeoutError:
            raise RuntimeError("Request timed out")
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Connection error: {str(e)}")
                
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
        self.connection_callbacks: Dict[str, Any] = {}
        
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
    
    def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """Get the status of a specific server."""
        if server_name not in self.connections:
            return {
                "status": MCPServerStatus.DISCONNECTED.value,
                "error_message": None,
                "capabilities": None,
                "tools": None,
                "resources": None,
                "prompts": None
            }
        
        connection = self.connections[server_name]
        return {
            "status": connection.status.value,
            "error_message": connection.error_message,
            "capabilities": connection.server.capabilities,
            "tools": connection.server.tools,
            "resources": connection.server.resources,
            "prompts": connection.server.prompts
        }
    
    def set_connection_callback(self, server_name: str, callback: Any):
        """Set a callback for connection status changes."""
        self.connection_callbacks[server_name] = callback
    
    async def _notify_status_change(self, server_name: str):
        """Notify about server status change."""
        if server_name in self.connection_callbacks:
            callback = self.connection_callbacks[server_name]
            if callback:
                status = self.get_server_status(server_name)
                await callback(server_name, status)


# Global instance
mcp_manager = MCPServerManager()