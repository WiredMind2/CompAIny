from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field

from .enums import TeamType


@dataclass
class Team:
    id: str
    name: str
    type: TeamType
    leader_id: str
    parent_team_id: Optional[str] = None
    member_ids: List[str] = field(default_factory=list)
    subteam_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_member(self, agent_id: str) -> None:
        if agent_id not in self.member_ids:
            self.member_ids.append(agent_id)
            self.updated_at = datetime.utcnow()

    def remove_member(self, agent_id: str) -> None:
        if agent_id in self.member_ids:
            self.member_ids.remove(agent_id)
            self.updated_at = datetime.utcnow()

    def add_subteam(self, subteam_id: str) -> None:
        if subteam_id not in self.subteam_ids:
            self.subteam_ids.append(subteam_id)
            self.updated_at = datetime.utcnow()

    def remove_subteam(self, subteam_id: str) -> None:
        if subteam_id in self.subteam_ids:
            self.subteam_ids.remove(subteam_id)
            self.updated_at = datetime.utcnow()

    def is_leader(self, agent_id: str) -> bool:
        return self.leader_id == agent_id

    def get_all_member_ids(self) -> List[str]:
        all_members = list(self.member_ids)
        return all_members