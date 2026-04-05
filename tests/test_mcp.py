import pytest
from src.mcp import MCPClient
from src.mcp.client import MCPTool, create_mcp_tools


class TestMCPClient:
    def test_mcp_client_init(self):
        client = MCPClient()
        assert client.server_url is None
        assert client.is_connected() is False

    def test_mcp_client_with_url(self):
        client = MCPClient(server_url="http://localhost:8080")
        assert client.server_url == "http://localhost:8080"

    def test_mcp_client_connect(self):
        client = MCPClient(server_url="http://localhost:8080")
        assert client.connect() is True
        assert client.is_connected() is True

    def test_mcp_client_disconnect(self):
        client = MCPClient(server_url="http://localhost:8080")
        client.connect()
        client.disconnect()
        assert client.is_connected() is False

    def test_mcp_client_from_env_empty(self, monkeypatch):
        monkeypatch.delenv("COMPANY_MCP_SERVERS", raising=False)
        client = MCPClient.from_env()
        assert client.server_url is None


class TestMCPTool:
    def test_mcp_tool_creation(self):
        tool = MCPTool(
            name="test_tool",
            description="Test tool description",
            input_schema={"type": "object", "properties": {}}
        )
        assert tool.name == "test_tool"
        assert tool.description == "Test tool description"

    def test_create_mcp_tools(self):
        tools = create_mcp_tools()
        assert "read_file" in tools
        assert "write_file" in tools
        assert "git" in tools


class TestMCPClientTools:
    def test_add_tool(self):
        client = MCPClient(server_url="http://localhost:8080")
        tool = MCPTool(name="test", description="desc", input_schema={})
        client.add_tool(tool)
        assert client.get_tool("test") == tool

    def test_get_tool_not_found(self):
        client = MCPClient()
        assert client.get_tool("nonexistent") is None

    def test_list_tools(self):
        client = MCPClient()
        tool1 = MCPTool(name="t1", description="d1", input_schema={})
        tool2 = MCPTool(name="t2", description="d2", input_schema={})
        client.add_tool(tool1)
        client.add_tool(tool2)
        assert len(client.list_tools()) == 2