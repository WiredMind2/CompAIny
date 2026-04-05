import os
from .base import Tool, ToolCategory, ToolResult


class WriteFileTool(Tool):
    def __init__(self):
        super().__init__(
            name="WriteFile",
            category=ToolCategory.WRITE,
            description="Write content to a file on the filesystem"
        )

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs.get("path")
        content = kwargs.get("content", "")
        append = kwargs.get("append", False)
        
        try:
            if path is None:
                return ToolResult(success=False, error="path parameter is required")
            
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            mode = 'a' if append else 'w'
            
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return ToolResult(success=True, data={
                "path": path,
                "bytes_written": len(content.encode('utf-8')),
                "mode": "appended" if append else "written"
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))