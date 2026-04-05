from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class MetricType(str, Enum):
    AGENT = "agent"
    TEAM = "team"


class TimeGranularity(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class MetricValue:
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    target: Optional[float] = None
    benchmark: Optional[float] = None


@dataclass
class AgentMetric:
    metric_id: str
    name: str
    description: str
    metric_type: MetricType = MetricType.AGENT
    values: List[MetricValue] = field(default_factory=list)
    unit: str = "count"

    def get_current(self) -> Optional[float]:
        if not self.values:
            return None
        return self.values[-1].value

    def get_average(self, days: int = 7) -> Optional[float]:
        if not self.values:
            return None
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        recent = [v.value for v in self.values if v.timestamp.timestamp() > cutoff]
        if not recent:
            return None
        return sum(recent) / len(recent)

    def get_trend(self, days: int = 7) -> Optional[float]:
        if not self.values or len(self.values) < 2:
            return None
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        recent = [v.value for v in self.values if v.timestamp.timestamp() > cutoff]
        if len(recent) < 2:
            return None
        half = len(recent) // 2
        first_half = sum(recent[:half]) / half
        second_half = sum(recent[half:]) / len(recent[half:])
        return second_half - first_half


@dataclass
class TeamMetric:
    metric_id: str
    name: str
    description: str
    metric_type: MetricType = MetricType.TEAM
    values: List[MetricValue] = field(default_factory=list)
    unit: str = "count"

    def get_current(self) -> Optional[float]:
        if not self.values:
            return None
        return self.values[-1].value

    def get_average(self, days: int = 7) -> Optional[float]:
        if not self.values:
            return None
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        recent = [v.value for v in self.values if v.timestamp.timestamp() > cutoff]
        if not recent:
            return None
        return sum(recent) / len(recent)

    def get_trend(self, days: int = 7) -> Optional[float]:
        if not self.values or len(self.values) < 2:
            return None
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        recent = [v.value for v in self.values if v.timestamp.timestamp() > cutoff]
        if len(recent) < 2:
            return None
        half = len(recent) // 2
        first_half = sum(recent[:half]) / half
        second_half = sum(recent[half:]) / len(recent[half:])
        return second_half - first_half


class AgentMetrics:
    TASKS_COMPLETED = "tasks_completed"
    TASK_VELOCITY = "task_velocity"
    TICKET_CYCLE_TIME = "ticket_cycle_time"
    CODE_REVIEW_TURNAROUND = "code_review_turnaround"
    BLOCKER_RESOLUTION_TIME = "blocker_resolution_time"
    COMMUNICATION_RESPONSE_TIME = "communication_response_time"
    MEETING_PARTICIPATION_RATE = "meeting_participation_rate"


class TeamMetrics:
    SPRINT_VELOCITY = "sprint_velocity"
    BACKLOG_CLEARANCE_RATE = "backlog_clearance_rate"
    TEAM_COLLABORATION_SCORE = "team_collaboration_score"
    BLOCKER_ESCALATION_FREQUENCY = "blocker_escalation_frequency"
    MEETING_EFFECTIVENESS = "meeting_effectiveness"
    QUALITY_SCORE = "quality_score"


AGENT_METRIC_DEFINITIONS = {
    AgentMetrics.TASKS_COMPLETED: AgentMetric(
        metric_id=AgentMetrics.TASKS_COMPLETED,
        name="Tasks Completed",
        description="Number of tasks completed by the agent",
        unit="tasks"
    ),
    AgentMetrics.TASK_VELOCITY: AgentMetric(
        metric_id=AgentMetrics.TASK_VELOCITY,
        name="Task Velocity",
        description="Rate of task completion over time",
        unit="tasks/day"
    ),
    AgentMetrics.TICKET_CYCLE_TIME: AgentMetric(
        metric_id=AgentMetrics.TICKET_CYCLE_TIME,
        name="Ticket Cycle Time",
        description="Average time from ticket start to completion",
        unit="hours"
    ),
    AgentMetrics.CODE_REVIEW_TURNAROUND: AgentMetric(
        metric_id=AgentMetrics.CODE_REVIEW_TURNAROUND,
        name="Code Review Turnaround",
        description="Average time to complete code reviews",
        unit="hours"
    ),
    AgentMetrics.BLOCKER_RESOLUTION_TIME: AgentMetric(
        metric_id=AgentMetrics.BLOCKER_RESOLUTION_TIME,
        name="Blocker Resolution Time",
        description="Average time to resolve blockers",
        unit="hours"
    ),
    AgentMetrics.COMMUNICATION_RESPONSE_TIME: AgentMetric(
        metric_id=AgentMetrics.COMMUNICATION_RESPONSE_TIME,
        name="Communication Response Time",
        description="Average time to respond to communications",
        unit="hours"
    ),
    AgentMetrics.MEETING_PARTICIPATION_RATE: AgentMetric(
        metric_id=AgentMetrics.MEETING_PARTICIPATION_RATE,
        name="Meeting Participation Rate",
        description="Rate of meeting participation",
        unit="percent"
    ),
}

TEAM_METRIC_DEFINITIONS = {
    TeamMetrics.SPRINT_VELOCITY: TeamMetric(
        metric_id=TeamMetrics.SPRINT_VELOCITY,
        name="Sprint Velocity",
        description="Story points completed per sprint",
        unit="points"
    ),
    TeamMetrics.BACKLOG_CLEARANCE_RATE: TeamMetric(
        metric_id=TeamMetrics.BACKLOG_CLEARANCE_RATE,
        name="Backlog Clearance Rate",
        description="Rate of backlog item completion",
        unit="percent"
    ),
    TeamMetrics.TEAM_COLLABORATION_SCORE: TeamMetric(
        metric_id=TeamMetrics.TEAM_COLLABORATION_SCORE,
        name="Team Collaboration Score",
        description="Score measuring team collaboration",
        unit="score"
    ),
    TeamMetrics.BLOCKER_ESCALATION_FREQUENCY: TeamMetric(
        metric_id=TeamMetrics.BLOCKER_ESCALATION_FREQUENCY,
        name="Blocker Escalation Frequency",
        description="Frequency of blocker escalations",
        unit="count"
    ),
    TeamMetrics.MEETING_EFFECTIVENESS: TeamMetric(
        metric_id=TeamMetrics.MEETING_EFFECTIVENESS,
        name="Meeting Effectiveness",
        description="Rating of meeting effectiveness",
        unit="rating"
    ),
    TeamMetrics.QUALITY_SCORE: TeamMetric(
        metric_id=TeamMetrics.QUALITY_SCORE,
        name="Quality Score",
        description="Quality score based on bugs per ticket",
        unit="score"
    ),
}