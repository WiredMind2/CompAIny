from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


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


@dataclass
class AgentMemory:
    short_term: dict = field(default_factory=dict)
    long_term: list = field(default_factory=list)


@dataclass
class Agent:
    id: str
    role: Role
    level: Level
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


@dataclass
class Team:
    id: str
    type: TeamType
    leader_id: str
    member_ids: list[str] = field(default_factory=list)

    def add_member(self, agent_id: str) -> None:
        if agent_id not in self.member_ids:
            self.member_ids.append(agent_id)

    def remove_member(self, agent_id: str) -> None:
        if agent_id in self.member_ids:
            self.member_ids.remove(agent_id)


@dataclass
class Ticket:
    id: str
    status: TicketStatus = TicketStatus.BACKLOG
    priority: TicketPriority = TicketPriority.MEDIUM
    assignee_id: Optional[str] = None
    github_issue_id: Optional[str] = None
    subtasks: list[str] = field(default_factory=list)
    complexity: Optional[int] = None
    locked_by: Optional[str] = None


@dataclass
class MeetingReport:
    author_id: str
    content: str


@dataclass
class Meeting:
    id: str
    type: MeetingType
    participant_ids: list[str] = field(default_factory=list)
    reports: list[MeetingReport] = field(default_factory=list)
    leader_id: Optional[str] = None

    def add_report(self, author_id: str, content: str) -> None:
        self.reports.append(MeetingReport(author_id=author_id, content=content))