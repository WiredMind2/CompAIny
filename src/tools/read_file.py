import os
from typing import Optional
from .base import Tool, ToolCategory, ToolResult


class ReadFileTool(Tool):
    def __init__(self):
        super().__init__(
            name="ReadFile",
            category=ToolCategory.READ,
            description="Read file contents from the filesystem"
        )

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs.get("path")
        offset = kwargs.get("offset", 1)
        limit = kwargs.get("limit")
        try:
            if path is None:
                return ToolResult(success=False, error="path parameter is required")
            
            if not os.path.exists(path):
                return ToolResult(success=False, error=f"File not found: {path}")
            
            if not os.path.isfile(path):
                return ToolResult(success=False, error=f"Not a file: {path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = offset - 1
            end = len(lines) if limit is None else start + limit
            
            content = ''.join(lines[start:end])
            
            return ToolResult(success=True, data={
                "path": path,
                "content": content,
                "total_lines": len(lines),
                "lines_returned": end - start
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))