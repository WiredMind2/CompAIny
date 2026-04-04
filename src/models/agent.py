from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field

from .enums import AgentRole, AgentLevel

if TYPE_CHECKING:
    from .company import Company


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
    
    def complete(self, company: "Company", prompt: str, model: str = "openai/gpt-3.5-turbo", **kwargs) -> str:
        """Generate a completion using the company's LLM provider."""
        return company.complete(prompt, model, **kwargs)
    
    def chat(self, company: "Company", messages: List[dict], model: str = "openai/gpt-3.5-turbo", **kwargs) -> str:
        """Generate a chat completion using the company's LLM provider."""
        return company.chat(messages, model, **kwargs)

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