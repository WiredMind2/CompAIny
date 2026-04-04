from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field

from .enums import AgentRole, AgentLevel


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