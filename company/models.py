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
    is_human: bool = False
    name: Optional[str] = None
    email: Optional[str] = None

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
class HumanAgentRegistry:
    human_agents: dict[str, Agent] = field(default_factory=dict)

    def register_human(
        self,
        agent_id: str,
        role: Role,
        level: Level,
        name: str,
        email: Optional[str] = None,
        team_id: Optional[str] = None,
        boss_id: Optional[str] = None,
    ) -> Agent:
        agent = Agent(
            id=agent_id,
            role=role,
            level=level,
            is_human=True,
            name=name,
            email=email,
            team_id=team_id,
            boss_id=boss_id,
        )
        self.human_agents[agent_id] = agent
        return agent

    def get_human(self, agent_id: str) -> Optional[Agent]:
        return self.human_agents.get(agent_id)

    def list_humans(self) -> list[Agent]:
        return list(self.human_agents.values())

    def unregister_human(self, agent_id: str) -> bool:
        if agent_id in self.human_agents:
            del self.human_agents[agent_id]
            return True
        return False


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
    github_issue_number: Optional[int] = None
    subtasks: list[str] = field(default_factory=list)
    complexity: Optional[int] = None
    locked_by: Optional[str] = None
    linked_prs: list[str] = field(default_factory=list)

    def link_pr(self, pr_id: str) -> None:
        if pr_id not in self.linked_prs:
            self.linked_prs.append(pr_id)

    def unlink_pr(self, pr_id: str) -> None:
        if pr_id in self.linked_prs:
            self.linked_prs.remove(pr_id)


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
