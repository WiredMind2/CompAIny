from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional


class ToolCategory(Enum):
    READ = "read"
    WRITE = "write"
    SEARCH = "search"
    EXECUTE = "execute"
    GIT = "git"
    BASH = "bash"


@dataclass
class ToolResult:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }


class Tool:
    def __init__(self, name: str, category: ToolCategory, description: str):
        self.name = name
        self.category = category
        self.description = description

    def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError("Subclasses must implement execute()")

    def get_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
        }