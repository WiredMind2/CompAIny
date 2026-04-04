from typing import Optional, List
from datetime import datetime


class Team:
    def __init__(
        self,
        id: str,
        name: str,
        leader_id: Optional[str] = None,
        member_ids: List[str] = None,
    ):
        self.id = id
        self.name = name
        self.leader_id = leader_id
        self.member_ids = member_ids or []
        self.created_at = datetime.utcnow()

    def add_member(self, agent_id: str) -> None:
        if agent_id not in self.member_ids:
            self.member_ids.append(agent_id)

    def remove_member(self, agent_id: str) -> bool:
        if agent_id in self.member_ids:
            self.member_ids.remove(agent_id)
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "leader_id": self.leader_id,
            "member_ids": self.member_ids,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        team = cls(
            id=data["id"],
            name=data["name"],
            leader_id=data.get("leader_id"),
            member_ids=data.get("member_ids", []),
        )
        if "created_at" in data:
            team.created_at = datetime.fromisoformat(data["created_at"])
        return team