import os
import glob as glob_module
from typing import List
from .base import Tool, ToolCategory, ToolResult


class GlobTool(Tool):
    def __init__(self):
        super().__init__(
            name="Glob",
            category=ToolCategory.SEARCH,
            description="Find files matching a pattern"
        )

    def execute(self, **kwargs) -> ToolResult:
        pattern = kwargs.get("pattern")
        base_path = kwargs.get("base_path", ".")
        
        try:
            if pattern is None:
                return ToolResult(success=False, error="pattern parameter is required")
            
            full_pattern = os.path.join(base_path, pattern)
            matches = glob_module.glob(full_pattern, recursive=True)
            
            relative_matches = []
            for m in matches:
                rel_path = os.path.relpath(m, base_path)
                relative_matches.append(rel_path)
            
            return ToolResult(success=True, data={
                "matches": relative_matches,
                "count": len(relative_matches)
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))