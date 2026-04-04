from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class MeetingType(Enum):
    DAILY_STANDUP = "daily_standup"
    SPRINT_PLANNING = "sprint_planning"
    RETROSPECTIVE = "retrospective"


class MeetingStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class MeetingReport:
    report_id: str
    meeting_id: str
    meeting_type: MeetingType
    created_at: datetime
    creator_id: str
    creator_name: str
    summary: str
    details: Dict[str, Any]
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    parent_report_id: Optional[str] = None
    propagated_to_parent: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "meeting_id": self.meeting_id,
            "meeting_type": self.meeting_type.value,
            "created_at": self.created_at.isoformat(),
            "creator_id": self.creator_id,
            "creator_name": self.creator_name,
            "summary": self.summary,
            "details": self.details,
            "action_items": self.action_items,
            "decisions": self.decisions,
            "parent_report_id": self.parent_report_id,
            "propagated_to_parent": self.propagated_to_parent
        }


@dataclass
class Meeting:
    meeting_id: str
    meeting_type: MeetingType
    title: str
    scheduled_at: datetime
    created_by: str
    team_id: str
    status: MeetingStatus = MeetingStatus.SCHEDULED
    participants: List[str] = field(default_factory=list)
    reports: List[MeetingReport] = field(default_factory=list)
    current_speaker: Optional[str] = None
    speaker_queue: List[str] = field(default_factory=list)
    sprint_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None

    def add_participant(self, agent_id: str) -> None:
        if agent_id not in self.participants:
            self.participants.append(agent_id)

    def remove_participant(self, agent_id: str) -> None:
        if agent_id in self.participants:
            self.participants.remove(agent_id)

    def start_meeting(self, starter_id: str) -> bool:
        if self.status != MeetingStatus.SCHEDULED:
            return False
        self.status = MeetingStatus.IN_PROGRESS
        return True

    def end_meeting(self) -> None:
        self.status = MeetingStatus.COMPLETED
        self.ended_at = datetime.now()

    def set_speaker_control(self, team_leader_id: str, speaker_id: Optional[str]) -> bool:
        if self.current_speaker != team_leader_id and self.current_speaker is not None:
            return False
        self.current_speaker = speaker_id
        return True

    def add_to_queue(self, agent_id: str) -> None:
        if agent_id not in self.speaker_queue:
            self.speaker_queue.append(agent_id)

    def next_speaker(self) -> Optional[str]:
        if self.speaker_queue:
            return self.speaker_queue.pop(0)
        return None

    def create_report(
        self,
        creator_id: str,
        creator_name: str,
        summary: str,
        details: Dict[str, Any],
        action_items: Optional[List[Dict[str, Any]]] = None,
        decisions: Optional[List[str]] = None,
        parent_report_id: Optional[str] = None
    ) -> MeetingReport:
        report = MeetingReport(
            report_id=str(uuid.uuid4()),
            meeting_id=self.meeting_id,
            meeting_type=self.meeting_type,
            created_at=datetime.now(),
            creator_id=creator_id,
            creator_name=creator_name,
            summary=summary,
            details=details,
            action_items=action_items or [],
            decisions=decisions or [],
            parent_report_id=parent_report_id
        )
        self.reports.append(report)
        return report


class DailyStandup(Meeting):
    def __init__(self, team_id: str, created_by: str, sprint_id: Optional[str] = None):
        super().__init__(
            meeting_id=str(uuid.uuid4()),
            meeting_type=MeetingType.DAILY_STANDUP,
            title=f"Daily Standup - {datetime.now().strftime('%Y-%m-%d')}",
            scheduled_at=datetime.now(),
            created_by=created_by,
            team_id=team_id,
            sprint_id=sprint_id
        )


class SprintPlanning(Meeting):
    def __init__(self, team_id: str, created_by: str, sprint_id: str):
        super().__init__(
            meeting_id=str(uuid.uuid4()),
            meeting_type=MeetingType.SPRINT_PLANNING,
            title=f"Sprint Planning - {sprint_id}",
            scheduled_at=datetime.now(),
            created_by=created_by,
            team_id=team_id,
            sprint_id=sprint_id
        )


class Retrospective(Meeting):
    def __init__(self, team_id: str, created_by: str, sprint_id: str):
        super().__init__(
            meeting_id=str(uuid.uuid4()),
            meeting_type=MeetingType.RETROSPECTIVE,
            title=f"Retrospective - {sprint_id}",
            scheduled_at=datetime.now(),
            created_by=created_by,
            team_id=team_id,
            sprint_id=sprint_id
        )