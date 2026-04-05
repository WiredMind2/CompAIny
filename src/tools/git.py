import subprocess
import os
from .base import Tool, ToolCategory, ToolResult


class GitTool(Tool):
    def __init__(self, repo_path: str = None):
        super().__init__(
            name="Git",
            category=ToolCategory.GIT,
            description="Execute git operations"
        )
        self.repo_path = repo_path

    def execute(self, **kwargs) -> ToolResult:
        args = kwargs.get("args", [])
        cwd = kwargs.get("cwd", self.repo_path)
        
        try:
            if not args:
                return ToolResult(success=False, error="args parameter is required")
            
            if cwd and not os.path.isdir(cwd):
                return ToolResult(success=False, error=f"Not a directory: {cwd}")
            
            cmd = ["git"] + args
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return ToolResult(success=True, data={
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            })
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Git command timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))