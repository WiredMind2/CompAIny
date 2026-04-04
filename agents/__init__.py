from enum import Enum
from typing import Optional
from datetime import datetime


class AgentRole(str, Enum):
    PO = "PO"
    DEVELOPER = "Developer"
    DESIGNER = "Designer"
    REVIEWER = "Reviewer"
    HR = "HR"
    CLIENT = "Client"


class AgentType(str, Enum):
    AI = "ai"
    HUMAN = "human"


class Agent:
    def __init__(
        self,
        id: str,
        name: str,
        role: AgentRole,
        level: int = 1,
        team_id: Optional[str] = None,
        boss_id: Optional[str] = None,
        agent_type: AgentType = AgentType.AI,
        memory: str = "",
    ):
        self.id = id
        self.name = name
        self.role = role
        self.level = level
        self.team_id = team_id
        self.boss_id = boss_id
        self.agent_type = agent_type
        self.memory = memory
        self.created_at = datetime.utcnow()

    def can_communicate_with(self, other: "Agent") -> bool:
        if self.id == other.id:
            return False
        level_diff = self.level - other.level
        return level_diff in [-1, 0, 1]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "level": self.level,
            "team_id": self.team_id,
            "boss_id": self.boss_id,
            "agent_type": self.agent_type.value,
            "memory": self.memory,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        agent = cls(
            id=data["id"],
            name=data["name"],
            role=AgentRole(data["role"]),
            level=data.get("level", 1),
            team_id=data.get("team_id"),
            boss_id=data.get("boss_id"),
            agent_type=AgentType(data.get("agent_type", "ai")),
            memory=data.get("memory", ""),
        )
        if "created_at" in data:
            agent.created_at = datetime.fromisoformat(data["created_at"])
        return agent