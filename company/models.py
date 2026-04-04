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
    name: str
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
        is_boss = other.boss_id == self.id
        is_underling = self.boss_id == other.id
        is_peer = other.level.value == self.level.value and other.team_id == self.team_id
        return is_boss or is_underling or is_peer

    def is_boss_of(self, other: Agent) -> bool:
        return other.level.value == self.level.value + 1 and other.boss_id == self.id

    def is_underling_of(self, other: Agent) -> bool:
        return other.level.value == self.level.value - 1 and self.boss_id == other.id

    def is_peer_of(self, other: Agent) -> bool:
        return other.level.value == self.level.value and other.id != self.id

    def get_boss(self, all_agents: dict[str, Agent]) -> Optional[Agent]:
        if self.boss_id and self.boss_id in all_agents:
            return all_agents[self.boss_id]
        return None

    def get_underlings(self, all_agents: dict[str, Agent]) -> list[Agent]:
        return [a for a in all_agents.values() if a.boss_id == self.id]

    def get_peers(self, all_agents: dict[str, Agent]) -> list[Agent]:
        return [a for a in all_agents.values() 
                if a.level.value == self.level.value 
                and a.id != self.id 
                and a.team_id == self.team_id]


class AgentFactory:
    _id_counter: int = 0

    @classmethod
    def create_agent(
        cls,
        name: str,
        role: Role,
        level: Level,
        team_id: Optional[str] = None,
        boss_id: Optional[str] = None,
        all_agents: Optional[dict[str, Agent]] = None,
    ) -> Agent:
        cls._id_counter += 1
        agent_id = f"agent_{cls._id_counter}"
        agent = Agent(
            id=agent_id,
            name=name,
            role=role,
            level=level,
            team_id=team_id,
            boss_id=boss_id,
        )
        if all_agents is not None:
            all_agents[agent_id] = agent
        return agent

    @classmethod
    def create_team_leader(
        cls,
        name: str,
        role: Role,
        team_id: str,
        level: Level = Level.L5,
        all_agents: Optional[dict[str, Agent]] = None,
    ) -> Agent:
        return cls.create_agent(
            name=name,
            role=role,
            level=level,
            team_id=team_id,
            boss_id=None,
            all_agents=all_agents,
        )

    @classmethod
    def create_underling(
        cls,
        name: str,
        role: Role,
        team_id: str,
        boss_id: str,
        level: Level = Level.L1,
        all_agents: Optional[dict[str, Agent]] = None,
    ) -> Agent:
        return cls.create_agent(
            name=name,
            role=role,
            level=level,
            team_id=team_id,
            boss_id=boss_id,
            all_agents=all_agents,
        )


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


@dataclass
class Message:
    id: str
    sender_id: str
    receiver_id: str
    content: str
    read: bool = False

    @classmethod
    def send(
        cls,
        sender: Agent,
        receiver: Agent,
        content: str,
        all_agents: dict[str, Agent],
    ) -> Optional[Message]:
        if not sender.can_communicate_with(receiver):
            return None
        Message._id_counter += 1
        return cls(
            id=f"msg_{Message._id_counter}",
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=content,
        )

    _id_counter: int = 0
