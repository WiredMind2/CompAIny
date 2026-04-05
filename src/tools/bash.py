import subprocess
from .base import Tool, ToolCategory, ToolResult


class BashTool(Tool):
    def __init__(self):
        super().__init__(
            name="Bash",
            category=ToolCategory.BASH,
            description="Execute shell commands"
        )

    def execute(self, **kwargs) -> ToolResult:
        command = kwargs.get("command")
        cwd = kwargs.get("cwd")
        
        try:
            if command is None:
                return ToolResult(success=False, error="command parameter is required")
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return ToolResult(success=True, data={
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            })
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Command timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))