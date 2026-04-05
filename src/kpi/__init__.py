from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from .metrics import (
    AgentMetric, TeamMetric, MetricValue, TimeGranularity,
    AgentMetrics, TeamMetrics,
    AGENT_METRIC_DEFINITIONS, TEAM_METRIC_DEFINITIONS
)
from .evaluator import (
    Evaluator, AgentEvaluation, TeamEvaluation,
    GoalTarget, ImprovementSuggestion
)
from .leaderboard import (
    Leaderboard, AgentRanking, TeamRanking,
    TrendAnalysis, MostImproved
)


@dataclass
class Event:
    type: str
    agent_id: Optional[str] = None
    team_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "agent_id": self.agent_id,
            "team_id": self.team_id,
            "timestamp": self.timestamp,
            **self.data
        }


@dataclass
class KPISummary:
    total_agents_evaluated: int
    total_teams_evaluated: int
    average_agent_score: float
    average_team_score: float
    top_performers: List[str]
    needs_improvement: List[str]


class KPIEngine:
    def __init__(self):
        self._evaluator = Evaluator()
        self._leaderboard = Leaderboard()
        self._events: List[Event] = []
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._teams: Dict[str, Dict[str, Any]] = {}

    def register_agent(self, agent_id: str, name: str, team_id: Optional[str] = None) -> None:
        self._agents[agent_id] = {
            "id": agent_id,
            "name": name,
            "team_id": team_id,
            "registered_at": datetime.utcnow()
        }

    def register_team(self, team_id: str, name: str) -> None:
        self._teams[team_id] = {
            "id": team_id,
            "name": name,
            "registered_at": datetime.utcnow()
        }

    def track_ticket_completed(
        self,
        agent_id: str,
        ticket_id: str,
        started_at: datetime,
        completed_at: datetime,
        has_bugs: bool = False,
        story_points: int = 0
    ) -> None:
        event = Event(
            type="ticket_completed",
            agent_id=agent_id,
            timestamp=completed_at,
            data={
                "ticket_id": ticket_id,
                "started_at": started_at,
                "completed_at": completed_at,
                "has_bugs": has_bugs,
                "story_points": story_points
            }
        )
        self._events.append(event)

    def track_code_review_completed(
        self,
        agent_id: str,
        review_id: str,
        started_at: datetime,
        completed_at: datetime
    ) -> None:
        event = Event(
            type="code_review_completed",
            agent_id=agent_id,
            timestamp=completed_at,
            data={
                "review_id": review_id,
                "started_at": started_at,
                "completed_at": completed_at
            }
        )
        self._events.append(event)

    def track_blocker_resolved(
        self,
        agent_id: str,
        blocker_id: str,
        reported_at: datetime,
        resolved_at: datetime
    ) -> None:
        event = Event(
            type="blocker_resolved",
            agent_id=agent_id,
            timestamp=resolved_at,
            data={
                "blocker_id": blocker_id,
                "reported_at": reported_at,
                "resolved_at": resolved_at
            }
        )
        self._events.append(event)

    def track_blocker_escalated(
        self,
        team_id: str,
        blocker_id: str,
        timestamp: datetime
    ) -> None:
        event = Event(
            type="blocker_escalated",
            team_id=team_id,
            timestamp=timestamp,
            data={"blocker_id": blocker_id}
        )
        self._events.append(event)

    def track_communication(
        self,
        agent_id: str,
        communication_id: str,
        received_at: datetime,
        responded_at: Optional[datetime] = None
    ) -> None:
        event = Event(
            type="communication_received" if not responded_at else "communication_responded",
            agent_id=agent_id,
            timestamp=received_at,
            data={
                "communication_id": communication_id,
                "received_at": received_at,
                "responded_at": responded_at
            }
        )
        self._events.append(event)

    def track_meeting_participation(
        self,
        agent_id: str,
        meeting_id: str,
        team_id: Optional[str] = None
    ) -> None:
        event = Event(
            type="meeting_participated",
            agent_id=agent_id,
            team_id=team_id,
            timestamp=datetime.utcnow(),
            data={"meeting_id": meeting_id}
        )
        self._events.append(event)

    def track_meeting_effectiveness(
        self,
        team_id: str,
        meeting_id: str,
        rating: float
    ) -> None:
        event = Event(
            type="meeting_effectiveness_rated",
            team_id=team_id,
            timestamp=datetime.utcnow(),
            data={
                "meeting_id": meeting_id,
                "rating": rating
            }
        )
        self._events.append(event)

    def track_sprint_completed(
        self,
        team_id: str,
        sprint_id: str,
        story_points: int
    ) -> None:
        event = Event(
            type="sprint_completed",
            team_id=team_id,
            timestamp=datetime.utcnow(),
            data={
                "sprint_id": sprint_id,
                "story_points": story_points
            }
        )
        self._events.append(event)

    def track_backlog_item(
        self,
        team_id: str,
        item_id: str,
        cleared: bool = False
    ) -> None:
        event_type = "backlog_item_cleared" if cleared else "backlog_item_added"
        event = Event(
            type=event_type,
            team_id=team_id,
            timestamp=datetime.utcnow(),
            data={"item_id": item_id}
        )
        self._events.append(event)

    def evaluate_agent(
        self,
        agent_id: str,
        days: int = 7,
        granularity: TimeGranularity = TimeGranularity.DAILY
    ) -> AgentEvaluation:
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=days)

        events = [e.to_dict() for e in self._events if e.agent_id == agent_id]

        return self._evaluator.evaluate_agent(
            agent_id=agent_id,
            period_start=period_start,
            period_end=period_end,
            events=events
        )

    def evaluate_team(
        self,
        team_id: str,
        days: int = 7,
        granularity: TimeGranularity = TimeGranularity.WEEKLY
    ) -> TeamEvaluation:
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=days)

        events = [e.to_dict() for e in self._events if e.team_id == team_id]

        return self._evaluator.evaluate_team(
            team_id=team_id,
            period_start=period_start,
            period_end=period_end,
            events=events
        )

    def evaluate_all_agents(
        self,
        days: int = 7
    ) -> List[AgentEvaluation]:
        evaluations = []
        for agent_id in self._agents:
            evaluation = self.evaluate_agent(agent_id, days)
            evaluations.append(evaluation)
        return evaluations

    def evaluate_all_teams(
        self,
        days: int = 7
    ) -> List[TeamEvaluation]:
        evaluations = []
        for team_id in self._teams:
            evaluation = self.evaluate_team(team_id, days)
            evaluations.append(evaluation)
        return evaluations

    def get_agent_leaderboard(
        self,
        days: int = 7,
        top_n: int = 10
    ) -> List[AgentRanking]:
        evaluations = self.evaluate_all_agents(days)
        return self._leaderboard.rank_agents(evaluations, top_n)

    def get_team_leaderboard(
        self,
        days: int = 7,
        top_n: int = 10
    ) -> List[TeamRanking]:
        evaluations = self.evaluate_all_teams(days)
        return self._leaderboard.rank_teams(evaluations, top_n)

    def get_top_performers_by_metric(
        self,
        metric_id: str,
        is_agent_metric: bool,
        top_n: int = 5
    ) -> List[Any]:
        if is_agent_metric:
            evaluations = self.evaluate_all_agents()
            return self._leaderboard.get_top_performers(metric_id, evaluations, top_n)
        else:
            evaluations = self.evaluate_all_teams()
            return self._leaderboard.get_top_performers(metric_id, evaluations, top_n)

    def get_most_improved(
        self,
        entity_type: str,
        days: int = 30
    ) -> List[MostImproved]:
        if entity_type == "agent":
            evaluations = self.evaluate_all_agents(days)
            return self._leaderboard.get_most_improved_agents(evaluations, days)
        else:
            evaluations = self.evaluate_all_teams(days)
            return self._leaderboard.get_most_improved_teams(evaluations, days)

    def analyze_trends(
        self,
        entity_type: str,
        metric_ids: List[str],
        days: int = 30
    ) -> List[TrendAnalysis]:
        if entity_type == "agent":
            evaluations = self.evaluate_all_agents()
            return self._leaderboard.analyze_trends(evaluations, metric_ids, days)
        else:
            evaluations = self.evaluate_all_teams()
            return self._leaderboard.analyze_trends(evaluations, metric_ids, days)

    def set_agent_goal(
        self,
        agent_id: str,
        metric_id: str,
        target_value: float
    ) -> None:
        self._evaluator.set_goal(agent_id, metric_id, target_value)

    def set_team_goal(
        self,
        team_id: str,
        metric_id: str,
        target_value: float
    ) -> None:
        self._evaluator.set_goal(team_id, metric_id, target_value)

    def check_goals(
        self,
        entity_id: str,
        is_agent: bool
    ) -> List[GoalTarget]:
        if is_agent:
            evaluation = self.evaluate_agent(entity_id)
            return self._evaluator.check_goals(entity_id, evaluation.metrics)
        else:
            evaluation = self.evaluate_team(entity_id)
            return self._evaluator.check_goals(entity_id, evaluation.metrics)

    def compare_entities(
        self,
        entity_type: str,
        entity_id_1: str,
        entity_id_2: str
    ) -> Dict[str, Any]:
        if entity_type == "agent":
            evaluations = self.evaluate_all_agents()
            return self._leaderboard.compare_agents(entity_id_1, entity_id_2, evaluations)
        else:
            evaluations = self.evaluate_all_teams()
            return self._leaderboard.compare_teams(entity_id_1, entity_id_2, evaluations)

    def get_summary(self, days: int = 7) -> KPISummary:
        agent_evals = self.evaluate_all_agents(days)
        team_evals = self.evaluate_all_teams(days)

        avg_agent_score = sum(e.score for e in agent_evals) / len(agent_evals) if agent_evals else 0
        avg_team_score = sum(e.score for e in team_evals) / len(team_evals) if team_evals else 0

        agent_rankings = self._leaderboard.rank_agents(agent_evals)
        top_performers = [r.agent_id for r in agent_rankings[:5]]
        needs_improvement = [r.agent_id for r in agent_rankings[-3:] if r.score < 60]

        return KPISummary(
            total_agents_evaluated=len(agent_evals),
            total_teams_evaluated=len(team_evals),
            average_agent_score=avg_agent_score,
            average_team_score=avg_team_score,
            top_performers=top_performers,
            needs_improvement=needs_improvement
        )

    def generate_auto_improvements(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[ImprovementSuggestion]:
        suggestions = []

        if entity_type == "agent":
            evaluation = self.evaluate_agent(entity_id)
            for rec in evaluation.recommendations:
                suggestions.append(ImprovementSuggestion(
                    category="agent_performance",
                    title="Performance Recommendation",
                    description=rec,
                    priority="medium",
                    estimated_impact="moderate"
                ))

            metrics = evaluation.metrics
            cycle_time = metrics.get(AgentMetrics.TICKET_CYCLE_TIME)
            if cycle_time and cycle_time.get_current() and cycle_time.get_current() > 48:
                suggestions.append(ImprovementSuggestion(
                    category="bottleneck",
                    title="High Cycle Time Detected",
                    description="Task completion time exceeds 48 hours. Consider breaking down tasks or removing blockers.",
                    priority="high",
                    estimated_impact="high",
                    related_metrics=[AgentMetrics.TICKET_CYCLE_TIME]
                ))

            velocity = metrics.get(AgentMetrics.TASK_VELOCITY)
            if velocity and velocity.get_trend() and velocity.get_trend() < -0.5:
                suggestions.append(ImprovementSuggestion(
                    category="workload",
                    title="Declining Velocity",
                    description="Task velocity is declining. Review workload balance and identify potential issues.",
                    priority="high",
                    estimated_impact="high",
                    related_metrics=[AgentMetrics.TASK_VELOCITY]
                ))

        else:
            evaluation = self.evaluate_team(entity_id)
            for rec in evaluation.recommendations:
                suggestions.append(ImprovementSuggestion(
                    category="team_performance",
                    title="Team Recommendation",
                    description=rec,
                    priority="medium",
                    estimated_impact="moderate"
                ))

            metrics = evaluation.metrics

            velocity = metrics.get(TeamMetrics.SPRINT_VELOCITY)
            if velocity and velocity.get_current() and velocity.get_current() < 20:
                suggestions.append(ImprovementSuggestion(
                    category="process",
                    title="Low Sprint Velocity",
                    description="Sprint velocity is below target. Consider refining estimation or removing blockers.",
                    priority="high",
                    estimated_impact="high",
                    related_metrics=[TeamMetrics.SPRINT_VELOCITY]
                ))

            escalations = metrics.get(TeamMetrics.BLOCKER_ESCALATION_FREQUENCY)
            if escalations and escalations.get_current() and escalations.get_current() > 3:
                suggestions.append(ImprovementSuggestion(
                    category="blockers",
                    title="High Blocker Escalation",
                    description="Too many blockers require escalation. Improve early detection and self-resolution.",
                    priority="high",
                    estimated_impact="high",
                    related_metrics=[TeamMetrics.BLOCKER_ESCALATION_FREQUENCY]
                ))

        return suggestions

    def suggest_workload_rebalancing(
        self,
        team_id: str
    ) -> Dict[str, Any]:
        evaluation = self.evaluate_team(team_id)

        agent_evaluations = []
        for agent_id in self._agents:
            if self._agents[agent_id].get("team_id") == team_id:
                agent_eval = self.evaluate_agent(agent_id)
                agent_evaluations.append({
                    "agent_id": agent_id,
                    "score": agent_eval.score,
                    "tasks_completed": agent_eval.metrics.get(AgentMetrics.TASKS_COMPLETED, AgentMetric("", "", "")).get_current() or 0
                })

        if not agent_evaluations:
            return {"message": "No agents in team"}

        avg_tasks = sum(a["tasks_completed"] for a in agent_evaluations) / len(agent_evaluations)
        overloaded = [a for a in agent_evaluations if a["tasks_completed"] > avg_tasks * 1.5]
        underloaded = [a for a in agent_evaluations if a["tasks_completed"] < avg_tasks * 0.5]

        recommendations = []
        if overloaded:
            recommendations.append(f"Consider redistributing work from {', '.join(a['agent_id'] for a in overloaded)}")
        if underloaded:
            recommendations.append(f"Consider assigning more tasks to {', '.join(a['agent_id'] for a in underloaded)}")

        return {
            "team_id": team_id,
            "average_tasks": avg_tasks,
            "overloaded_agents": overloaded,
            "underloaded_agents": underloaded,
            "recommendations": recommendations
        }

    def get_aggregated_metrics(
        self,
        entity_type: str,
        granularity: TimeGranularity = TimeGranularity.DAILY,
        days: int = 30
    ) -> Dict[str, List[MetricValue]]:
        result = {}

        if entity_type == "agent":
            evaluations = self.evaluate_all_agents(days)
            for metric_id in AgentMetrics:
                values = []
                for eval in evaluations:
                    if metric_id in eval.metrics:
                        metric = eval.metrics[metric_id]
                        values.extend(metric.values)
                result[metric_id] = values
        else:
            evaluations = self.evaluate_all_teams(days)
            for metric_id in TeamMetrics:
                values = []
                for eval in evaluations:
                    if metric_id in eval.metrics:
                        metric = eval.metrics[metric_id]
                        values.extend(metric.values)
                result[metric_id] = values

        return result


__all__ = [
    "KPIEngine",
    "Event",
    "KPISummary",
    "AgentMetric",
    "TeamMetric",
    "MetricValue",
    "AgentMetrics",
    "TeamMetrics",
    "TimeGranularity",
    "AgentEvaluation",
    "TeamEvaluation",
    "GoalTarget",
    "ImprovementSuggestion",
    "Leaderboard",
    "AgentRanking",
    "TeamRanking",
    "TrendAnalysis",
    "MostImproved",
    "Evaluator",
]