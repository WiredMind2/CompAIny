from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from .enums import AgentRole, AgentLevel


@dataclass
class ToolCall:
    id: str
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None


@dataclass
class Agent:
    id: str
    name: str
    role: AgentRole
    level: AgentLevel
    team_id: Optional[str] = None
    boss_id: Optional[str] = None
    memory_short_term: dict = field(default_factory=dict)
    memory_long_term: List[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    workspace_path: Optional[str] = None
    workspace_branch: Optional[str] = None
    repo_url: Optional[str] = None
    llm_provider: Optional[Any] = None

    def can_message(self, target: "Agent") -> bool:
        if target.id == self.id:
            return False
        if target.id == self.boss_id:
            return True
        if self.boss_id == target.id:
            return True
        if target.team_id == self.team_id and target.team_id is not None:
            return True
        return False

    def get_role_level(self) -> int:
        return self.level.value

    def get_reporting_chain(self) -> List[str]:
        return []

    def set_workspace(self, repo_url: str, branch: str, workspace_path: str):
        self.repo_url = repo_url
        self.workspace_branch = branch
        self.workspace_path = workspace_path

    def execute_tool(self, tool: Any, **kwargs) -> Dict[str, Any]:
        result = tool.execute(**kwargs)
        return result.to_dict()

    def store_tool_result(self, tool_call_id: str, result: Dict[str, Any]):
        self.memory_short_term[tool_call_id] = result

    def set_llm_provider(self, provider: Any) -> None:
        self.llm_provider = provider

    def complete(self, prompt: str, model: str = "openai/gpt-3.5-turbo", **kwargs) -> str:
        if self.llm_provider:
            return self.llm_provider.complete(prompt, model, **kwargs)
        raise Exception("No LLM provider configured")

    def chat(self, messages: List[Dict[str, str]], model: str = "openai/gpt-3.5-turbo", **kwargs) -> str:
        if self.llm_provider:
            return self.llm_provider.chat(messages, model, **kwargs)
        raise Exception("No LLM provider configured")