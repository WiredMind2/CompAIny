import pytest
import os
import tempfile
import shutil
from src.tools import (
    Tool,
    ToolCategory,
    ToolResult,
    ReadFileTool,
    WriteFileTool,
    GrepTool,
    BashTool,
    GitTool,
    GlobTool,
)


class TestToolCategory:
    def test_tool_category_values(self):
        assert ToolCategory.READ.value == "read"
        assert ToolCategory.WRITE.value == "write"
        assert ToolCategory.SEARCH.value == "search"
        assert ToolCategory.EXECUTE.value == "execute"
        assert ToolCategory.GIT.value == "git"
        assert ToolCategory.BASH.value == "bash"


class TestToolResult:
    def test_tool_result_success(self):
        result = ToolResult(success=True, data={"key": "value"})
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None

    def test_tool_result_failure(self):
        result = ToolResult(success=False, error="Something went wrong")
        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.data is None

    def test_tool_result_to_dict(self):
        result = ToolResult(success=True, data={"key": "value"})
        d = result.to_dict()
        assert d["success"] is True
        assert d["data"] == {"key": "value"}


class TestToolBase:
    def test_tool_init(self):
        tool = Tool(name="TestTool", category=ToolCategory.READ, description="Test description")
        assert tool.name == "TestTool"
        assert tool.category == ToolCategory.READ
        assert tool.description == "Test description"

    def test_tool_get_schema(self):
        tool = Tool(name="TestTool", category=ToolCategory.READ, description="Test description")
        schema = tool.get_schema()
        assert schema["name"] == "TestTool"
        assert schema["category"] == "read"
        assert schema["description"] == "Test description"


class TestReadFileTool:
    def test_read_file_success(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World\nLine 2\nLine 3")
        
        tool = ReadFileTool()
        result = tool.execute(path=str(test_file))
        
        assert result.success is True
        assert "Hello World" in result.data["content"]

    def test_read_file_not_found(self):
        tool = ReadFileTool()
        result = tool.execute(path="/nonexistent/file.txt")
        
        assert result.success is False
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_read_file_missing_path(self):
        tool = ReadFileTool()
        result = tool.execute()
        
        assert result.success is False
        assert result.error is not None
        assert "required" in result.error.lower()


class TestWriteFileTool:
    def test_write_file_success(self, tmp_path):
        test_file = tmp_path / "output.txt"
        
        tool = WriteFileTool()
        result = tool.execute(path=str(test_file), content="Test content")
        
        assert result.success is True
        assert test_file.read_text() == "Test content"

    def test_write_file_missing_path(self):
        tool = WriteFileTool()
        result = tool.execute(content="Test")
        
        assert result.success is False
        assert "required" in result.error.lower()

    def test_write_file_append(self, tmp_path):
        test_file = tmp_path / "output.txt"
        test_file.write_text("Initial\n")
        
        tool = WriteFileTool()
        result = tool.execute(path=str(test_file), content="Appended", append=True)
        
        assert result.success is True
        assert test_file.read_text() == "Initial\nAppended"


class TestGrepTool:
    def test_grep_found(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo():\n    return True\ndef bar():\n    pass")
        
        tool = GrepTool()
        result = tool.execute(pattern="def", path=str(tmp_path))
        
        assert result.success is True
        assert result.data["count"] >= 2

    def test_grep_not_found(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("No matching patterns here")
        
        tool = GrepTool()
        result = tool.execute(pattern="xyz123", path=str(tmp_path))
        
        assert result.success is True
        assert result.data["count"] == 0

    def test_grep_missing_pattern(self):
        tool = GrepTool()
        result = tool.execute(path=".")
        
        assert result.success is False
        assert "required" in result.error.lower()


class TestBashTool:
    def test_bash_echo(self):
        tool = BashTool()
        result = tool.execute(command="echo 'hello'")
        
        assert result.success is True
        assert "hello" in result.data["stdout"]

    def test_bash_returncode(self):
        tool = BashTool()
        result = tool.execute(command="exit 1")
        
        assert result.success is True
        assert result.data["returncode"] == 1

    def test_bash_missing_command(self):
        tool = BashTool()
        result = tool.execute()
        
        assert result.success is False
        assert "required" in result.error.lower()


class TestGitTool:
    def test_git_version(self):
        tool = GitTool()
        result = tool.execute(args=["--version"])
        
        assert result.success is True
        assert "git" in result.data["stdout"].lower()

    def test_git_missing_args(self):
        tool = GitTool()
        result = tool.execute()
        
        assert result.success is False
        assert "required" in result.error.lower()


class TestGlobTool:
    def test_glob_found(self, tmp_path):
        (tmp_path / "test1.py").touch()
        (tmp_path / "test2.py").touch()
        (tmp_path / "other.txt").touch()
        
        tool = GlobTool()
        result = tool.execute(pattern="*.py", base_path=str(tmp_path))
        
        assert result.success is True
        assert result.data["count"] == 2

    def test_glob_missing_pattern(self):
        tool = GlobTool()
        result = tool.execute(base_path=".")
        
        assert result.success is False
        assert "required" in result.error.lower()