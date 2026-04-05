import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: dict


class MCPClient:
    def __init__(self, server_url: str = None):
        self.server_url = server_url
        self.tools: Dict[str, MCPTool] = {}
        self._connected = False

    def connect(self) -> bool:
        if not self.server_url:
            self._connected = False
            return False
        self._connected = True
        return True

    def disconnect(self):
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def add_tool(self, tool: MCPTool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[MCPTool]:
        return self.tools.get(name)

    def list_tools(self) -> List[MCPTool]:
        return list(self.tools.values())

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        if not self.is_connected():
            return {"error": "Not connected to MCP server"}
        
        tool = self.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool not found: {tool_name}"}
        
        return {"success": True, "result": "MCP tool execution not implemented in mock"}

    @staticmethod
    def from_env() -> "MCPClient":
        servers_config = os.environ.get("COMPANY_MCP_SERVERS")
        if not servers_config:
            return MCPClient()
        
        try:
            servers = json.loads(servers_config)
            if servers:
                return MCPClient(server_url=servers[0].get("url"))
        except json.JSONDecodeError:
            pass
        
        return MCPClient()


def create_mcp_tools() -> Dict[str, MCPTool]:
    return {
        "read_file": MCPTool(
            name="read_file",
            description="Read contents of a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"]
            }
        ),
        "write_file": MCPTool(
            name="write_file",
            description="Write content to a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        ),
        "git": MCPTool(
            name="git",
            description="Execute git commands",
            input_schema={
                "type": "object",
                "properties": {
                    "args": {"type": "array", "items": {"type": "string"}, "description": "Git arguments"}
                },
                "required": ["args"]
            }
        ),
    }