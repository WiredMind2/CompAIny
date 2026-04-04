from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


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


class TicketDecision(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEFERRED = "deferred"


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
class SprintPlanningItem:
    ticket_id: str
    subtasks: list[str] = field(default_factory=list)
    complexity: Optional[int] = None
    decision: Optional[TicketDecision] = None
    recruiter_id: Optional[str] = None


@dataclass
class DailyStandupReport:
    agent_id: str
    progress: str
    blockers: list[str] = field(default_factory=list)


@dataclass
class RetrospectiveReport:
    agent_id: str
    what_went_well: list[str] = field(default_factory=list)
    what_to_improve: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)


@dataclass
class MeetingReport:
    author_id: str
    content: str
    daily_standup: Optional[DailyStandupReport] = None
    sprint_planning: Optional[SprintPlanningItem] = None
    retrospective: Optional[RetrospectiveReport] = None


@dataclass
class Meeting:
    id: str
    type: MeetingType
    participant_ids: list[str] = field(default_factory=list)
    reports: list[MeetingReport] = field(default_factory=list)
    leader_id: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    current_speaker_id: Optional[str] = None

    def add_report(self, author_id: str, content: str) -> None:
        self.reports.append(MeetingReport(author_id=author_id, content=content))

    def add_daily_standup_report(self, agent_id: str, progress: str, blockers: list[str]) -> None:
        report = MeetingReport(
            author_id=agent_id,
            content=f"Progress: {progress}, Blockers: {', '.join(blockers) if blockers else 'none'}",
            daily_standup=DailyStandupReport(agent_id=agent_id, progress=progress, blockers=blockers)
        )
        self.reports.append(report)

    def add_sprint_planning_item(self, ticket_id: str, subtasks: list[str], complexity: Optional[int] = None) -> None:
        item = SprintPlanningItem(ticket_id=ticket_id, subtasks=subtasks, complexity=complexity)
        report = MeetingReport(
            author_id=self.leader_id or "",
            content=f"Sprint planning for ticket {ticket_id}: {len(subtasks)} subtasks, complexity {complexity}",
            sprint_planning=item
        )
        self.reports.append(report)

    def decide_ticket(self, ticket_id: str, decision: TicketDecision, recruiter_id: Optional[str] = None) -> None:
        for report in self.reports:
            if report.sprint_planning and report.sprint_planning.ticket_id == ticket_id:
                report.sprint_planning.decision = decision
                report.sprint_planning.recruiter_id = recruiter_id
                return

    def add_retrospective_report(self, agent_id: str, what_went_well: list[str], what_to_improve: list[str], action_items: list[str]) -> None:
        report = MeetingReport(
            author_id=agent_id,
            content=f"Well: {what_went_well}, Improve: {what_to_improve}, Actions: {action_items}",
            retrospective=RetrospectiveReport(
                agent_id=agent_id,
                what_went_well=what_went_well,
                what_to_improve=what_to_improve,
                action_items=action_items
            )
        )
        self.reports.append(report)

    def set_current_speaker(self, speaker_id: str, leader_id: str) -> bool:
        if leader_id != self.leader_id:
            return False
        self.current_speaker_id = speaker_id
        return True

    def can_speak(self, agent_id: str) -> bool:
        if self.current_speaker_id is None:
            return True
        return agent_id == self.current_speaker_id

    def propagate_to_parent(self, parent_leader_id: str) -> Meeting:
        parent_meeting = Meeting(
            id=str(uuid.uuid4()),
            type=self.type,
            leader_id=parent_leader_id
        )
        parent_meeting.participant_ids = [parent_leader_id]
        
        summary_parts = []
        for report in self.reports:
            if self.type == MeetingType.DAILY_STANDUP and report.daily_standup:
                summary_parts.append(f"{report.author_id}: {report.daily_standup.progress}")
            elif self.type == MeetingType.SPRINT_PLANNING and report.sprint_planning:
                decision = report.sprint_planning.decision.name if report.sprint_planning.decision else "pending"
                summary_parts.append(f"ticket {report.sprint_planning.ticket_id}: {decision}")
            elif self.type == MeetingType.RETROSPECTIVE and report.retrospective:
                summary_parts.append(f"{report.author_id}: {len(report.retrospective.action_items)} action items")
        
        parent_meeting.add_report(self.leader_id or "", f"Child team report: {'; '.join(summary_parts)}")
        return parent_meeting
