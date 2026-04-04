from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class Role(Enum):
    PO = "product_owner"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    REVIEWER = "reviewer"
    HR = "hr"
    CLIENT = "client"


class Level(Enum):
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6
    L7 = 7
    L8 = 8
    L9 = 9
    L10 = 10


class TicketStatus(Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TeamType(Enum):
    PRODUCT = "product"
    ENGINEERING = "engineering"
    DESIGN = "design"
    OPERATIONS = "operations"
    EXECUTIVE = "executive"


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
class AgentMemory:
    short_term: Dict[str, Any] = field(default_factory=dict)
    long_term: list = field(default_factory=list)


@dataclass
class Agent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: Role = Role.DEVELOPER
    level: Level = Level.L1
    team_id: Optional[str] = None
    memory: AgentMemory = field(default_factory=AgentMemory)
    boss_id: Optional[str] = None

    def can_communicate_with(self, other: Agent) -> bool:
        if self.id == other.id:
            return False
        my_level = self.level.value
        other_level = other.level.value
        return other_level in (my_level + 1, my_level, my_level - 1)

    def is_boss_of(self, other: Agent) -> bool:
        return other.level.value == self.level.value + 1

    def is_underling_of(self, other: Agent) -> bool:
        return other.level.value == self.level.value - 1

    def is_peer_of(self, other: Agent) -> bool:
        return other.level.value == self.level.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "level": self.level.value,
            "team_id": self.team_id,
            "boss_id": self.boss_id,
            "memory": {
                "short_term": self.memory.short_term,
                "long_term": self.memory.long_term
            }
        }


@dataclass
class Team:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: TeamType = TeamType.ENGINEERING
    leader_id: str = ""
    parent_team_id: Optional[str] = None
    member_ids: list[str] = field(default_factory=list)
    subteam_ids: list[str] = field(default_factory=list)
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

    def is_leader(self, agent_id: str) -> bool:
        return self.leader_id == agent_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "leader_id": self.leader_id,
            "parent_team_id": self.parent_team_id,
            "member_ids": self.member_ids,
            "subteam_ids": self.subteam_ids,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Ticket:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: TicketStatus = TicketStatus.BACKLOG
    priority: TicketPriority = TicketPriority.MEDIUM
    assignee_id: Optional[str] = None
    github_issue_id: Optional[str] = None
    subtasks: list[str] = field(default_factory=list)
    complexity: Optional[int] = None
    locked_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assignee_id": self.assignee_id,
            "github_issue_id": self.github_issue_id,
            "subtasks": self.subtasks,
            "complexity": self.complexity,
            "locked_by": self.locked_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class MeetingReport:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str = ""
    meeting_type: MeetingType = MeetingType.DAILY_STANDUP
    created_at: datetime = field(default_factory=datetime.utcnow)
    author_id: str = ""
    author_name: str = ""
    summary: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    action_items: list[Dict[str, Any]] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    parent_report_id: Optional[str] = None
    propagated_to_parent: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "meeting_id": self.meeting_id,
            "meeting_type": self.meeting_type.value,
            "created_at": self.created_at.isoformat(),
            "author_id": self.author_id,
            "author_name": self.author_name,
            "summary": self.summary,
            "details": self.details,
            "action_items": self.action_items,
            "decisions": self.decisions,
            "parent_report_id": self.parent_report_id,
            "propagated_to_parent": self.propagated_to_parent
        }


@dataclass
class Meeting:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MeetingType = MeetingType.DAILY_STANDUP
    title: str = ""
    scheduled_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    team_id: str = ""
    status: MeetingStatus = MeetingStatus.SCHEDULED
    participant_ids: list[str] = field(default_factory=list)
    reports: list[MeetingReport] = field(default_factory=list)
    current_speaker: Optional[str] = None
    speaker_queue: list[str] = field(default_factory=list)
    sprint_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

    def add_participant(self, agent_id: str) -> None:
        if agent_id not in self.participant_ids:
            self.participant_ids.append(agent_id)

    def remove_participant(self, agent_id: str) -> None:
        if agent_id in self.participant_ids:
            self.participant_ids.remove(agent_id)

    def start_meeting(self, starter_id: str) -> bool:
        if self.status != MeetingStatus.SCHEDULED:
            return False
        self.status = MeetingStatus.IN_PROGRESS
        return True

    def end_meeting(self) -> None:
        self.status = MeetingStatus.COMPLETED
        self.ended_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "scheduled_at": self.scheduled_at.isoformat(),
            "created_by": self.created_by,
            "team_id": self.team_id,
            "status": self.status.value,
            "participant_ids": self.participant_ids,
            "reports": [r.to_dict() for r in self.reports],
            "current_speaker": self.current_speaker,
            "speaker_queue": self.speaker_queue,
            "sprint_id": self.sprint_id,
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }