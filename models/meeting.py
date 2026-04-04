from enum import Enum
from typing import Optional, List
from datetime import datetime


class MeetingType(str, Enum):
    STANDUP = "standup"
    PLANNING = "planning"
    RETROSPECTIVE = "retrospective"


class Meeting:
    def __init__(
        self,
        id: str,
        meeting_type: MeetingType,
        host_id: str,
        participant_ids: List[str] = None,
        ticket_ids: List[str] = None,
    ):
        self.id = id
        self.meeting_type = meeting_type
        self.host_id = host_id
        self.participant_ids = participant_ids or []
        self.ticket_ids = ticket_ids or []
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self.report: str = ""

    def add_participant(self, agent_id: str) -> None:
        if agent_id not in self.participant_ids:
            self.participant_ids.append(agent_id)

    def remove_participant(self, agent_id: str) -> bool:
        if agent_id in self.participant_ids:
            self.participant_ids.remove(agent_id)
            return True
        return False

    def complete(self, report: str) -> None:
        self.report = report
        self.completed_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "meeting_type": self.meeting_type.value,
            "host_id": self.host_id,
            "participant_ids": self.participant_ids,
            "ticket_ids": self.ticket_ids,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "report": self.report,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Meeting":
        meeting = cls(
            id=data["id"],
            meeting_type=MeetingType(data["meeting_type"]),
            host_id=data["host_id"],
            participant_ids=data.get("participant_ids", []),
            ticket_ids=data.get("ticket_ids", []),
        )
        if "created_at" in data:
            meeting.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("completed_at"):
            meeting.completed_at = datetime.fromisoformat(data["completed_at"])
        meeting.report = data.get("report", "")
        return meeting