import os
import re
from typing import List
from .base import Tool, ToolCategory, ToolResult


class GrepTool(Tool):
    def __init__(self):
        super().__init__(
            name="Grep",
            category=ToolCategory.SEARCH,
            description="Search for patterns in files"
        )

    def execute(self, **kwargs) -> ToolResult:
        pattern = kwargs.get("pattern")
        path = kwargs.get("path", ".")
        
        try:
            if pattern is None:
                return ToolResult(success=False, error="pattern parameter is required")
            
            results: List[dict] = []
            regex = re.compile(pattern)
            
            if os.path.isfile(path):
                files_to_search = [path]
            elif os.path.isdir(path):
                files_to_search = []
                for root, _, files in os.walk(path):
                    for f in files:
                        if f.endswith(('.py', '.js', '.ts', '.txt', '.md', '.json', '.yaml', '.yml')):
                            files_to_search.append(os.path.join(root, f))
            else:
                return ToolResult(success=False, error=f"Invalid path: {path}")
            
            for filepath in files_to_search:
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "file": filepath,
                                    "line": line_num,
                                    "content": line.rstrip()
                                })
                except Exception:
                    continue
            
            return ToolResult(success=True, data={
                "matches": results,
                "count": len(results)
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))