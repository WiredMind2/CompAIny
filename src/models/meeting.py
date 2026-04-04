from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class MeetingType(str, Enum):
    STANDUP = "standup"
    PLANNING = "planning"
    RETROSPECTIVE = "retrospective"
    REVIEW = "review"


@dataclass
class Meeting:
    id: str
    type: MeetingType
    team_id: str
    host_id: str
    participant_ids: List[str] = field(default_factory=list)
    reports: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def add_participant(self, agent_id: str) -> None:
        if agent_id not in self.participant_ids:
            self.participant_ids.append(agent_id)

    def remove_participant(self, agent_id: str) -> bool:
        if agent_id in self.participant_ids:
            self.participant_ids.remove(agent_id)
            return True
        return False

    def add_report(self, report: str) -> None:
        self.reports.append(report)

    def complete(self) -> None:
        self.completed_at = datetime.utcnow()