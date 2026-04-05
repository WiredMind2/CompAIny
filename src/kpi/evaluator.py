from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .metrics import (
    AgentMetric, TeamMetric, AgentMetrics, TeamMetrics,
    MetricValue, TimeGranularity, AGENT_METRIC_DEFINITIONS, TEAM_METRIC_DEFINITIONS
)


@dataclass
class AgentEvaluation:
    agent_id: str
    period_start: datetime
    period_end: datetime
    metrics: Dict[str, AgentMetric] = field(default_factory=dict)
    score: float = 0.0
    grade: str = "N/A"
    recommendations: List[str] = field(default_factory=list)


@dataclass
class TeamEvaluation:
    team_id: str
    period_start: datetime
    period_end: datetime
    metrics: Dict[str, TeamMetric] = field(default_factory=dict)
    score: float = 0.0
    grade: str = "N/A"
    recommendations: List[str] = field(default_factory=list)


@dataclass
class GoalTarget:
    metric_id: str
    target_value: float
    current_value: float = 0.0
    achieved: bool = False

    def check_achievement(self) -> bool:
        self.achieved = self.current_value >= self.target_value
        return self.achieved


@dataclass
class ImprovementSuggestion:
    category: str
    title: str
    description: str
    priority: str = "medium"
    estimated_impact: str = "moderate"
    related_metrics: List[str] = field(default_factory=list)


class Evaluator:
    def __init__(self):
        self._agent_metrics: Dict[str, Dict[str, AgentMetric]] = {}
        self._team_metrics: Dict[str, Dict[str, TeamMetric]] = {}
        self._goals: Dict[str, List[GoalTarget]] = {}

    def calculate_agent_score(
        self,
        agent_id: str,
        metrics: Dict[str, AgentMetric]
    ) -> float:
        weights = {
            AgentMetrics.TASKS_COMPLETED: 0.25,
            AgentMetrics.TASK_VELOCITY: 0.20,
            AgentMetrics.TICKET_CYCLE_TIME: 0.15,
            AgentMetrics.CODE_REVIEW_TURNAROUND: 0.15,
            AgentMetrics.BLOCKER_RESOLUTION_TIME: 0.10,
            AgentMetrics.COMMUNICATION_RESPONSE_TIME: 0.10,
            AgentMetrics.MEETING_PARTICIPATION_RATE: 0.05,
        }

        score = 0.0
        total_weight = 0.0

        for metric_id, weight in weights.items():
            if metric_id in metrics:
                metric = metrics[metric_id]
                current = metric.get_current()
                avg = metric.get_average()

                if current is not None and metric_id == AgentMetrics.TICKET_CYCLE_TIME:
                    score += (1.0 / (1.0 + current / 24.0)) * weight
                    total_weight += weight
                elif current is not None and metric_id == AgentMetrics.CODE_REVIEW_TURNAROUND:
                    score += (1.0 / (1.0 + current / 24.0)) * weight
                    total_weight += weight
                elif current is not None and metric_id == AgentMetrics.BLOCKER_RESOLUTION_TIME:
                    score += (1.0 / (1.0 + current / 24.0)) * weight
                    total_weight += weight
                elif current is not None and metric_id == AgentMetrics.COMMUNICATION_RESPONSE_TIME:
                    score += (1.0 / (1.0 + current / 24.0)) * weight
                    total_weight += weight
                elif current is not None:
                    score += min(current / 10.0, 1.0) * weight
                    total_weight += weight
                elif avg is not None:
                    if metric_id == AgentMetrics.TICKET_CYCLE_TIME:
                        score += (1.0 / (1.0 + avg / 24.0)) * weight
                    elif metric_id == AgentMetrics.CODE_REVIEW_TURNAROUND:
                        score += (1.0 / (1.0 + avg / 24.0)) * weight
                    elif metric_id == AgentMetrics.BLOCKER_RESOLUTION_TIME:
                        score += (1.0 / (1.0 + avg / 24.0)) * weight
                    elif metric_id == AgentMetrics.COMMUNICATION_RESPONSE_TIME:
                        score += (1.0 / (1.0 + avg / 24.0)) * weight
                    else:
                        score += min(avg / 10.0, 1.0) * weight
                    total_weight += weight

        if total_weight > 0:
            score = score / total_weight

        return min(score * 100.0, 100.0)

    def calculate_team_score(
        self,
        team_id: str,
        metrics: Dict[str, TeamMetric]
    ) -> float:
        weights = {
            TeamMetrics.SPRINT_VELOCITY: 0.25,
            TeamMetrics.BACKLOG_CLEARANCE_RATE: 0.20,
            TeamMetrics.TEAM_COLLABORATION_SCORE: 0.15,
            TeamMetrics.BLOCKER_ESCALATION_FREQUENCY: 0.15,
            TeamMetrics.MEETING_EFFECTIVENESS: 0.10,
            TeamMetrics.QUALITY_SCORE: 0.15,
        }

        score = 0.0
        total_weight = 0.0

        for metric_id, weight in weights.items():
            if metric_id in metrics:
                metric = metrics[metric_id]
                current = metric.get_current()
                avg = metric.get_average()

                if current is not None and metric_id == TeamMetrics.BLOCKER_ESCALATION_FREQUENCY:
                    score += max(1.0 - current / 5.0, 0.0) * weight
                    total_weight += weight
                elif current is not None:
                    score += min(current / 100.0, 1.0) * weight
                    total_weight += weight
                elif avg is not None:
                    if metric_id == TeamMetrics.BLOCKER_ESCALATION_FREQUENCY:
                        score += max(1.0 - avg / 5.0, 0.0) * weight
                    else:
                        score += min(avg / 100.0, 1.0) * weight
                    total_weight += weight

        if total_weight > 0:
            score = score / total_weight

        return min(score * 100.0, 100.0)

    def grade_score(self, score: float) -> str:
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def evaluate_agent(
        self,
        agent_id: str,
        period_start: datetime,
        period_end: datetime,
        events: List[Dict[str, Any]]
    ) -> AgentEvaluation:
        metrics = self._calculate_agent_metrics(agent_id, period_start, period_end, events)
        score = self.calculate_agent_score(agent_id, metrics)
        grade = self.grade_score(score)
        recommendations = self._generate_agent_recommendations(agent_id, metrics)

        return AgentEvaluation(
            agent_id=agent_id,
            period_start=period_start,
            period_end=period_end,
            metrics=metrics,
            score=score,
            grade=grade,
            recommendations=recommendations
        )

    def evaluate_team(
        self,
        team_id: str,
        period_start: datetime,
        period_end: datetime,
        events: List[Dict[str, Any]]
    ) -> TeamEvaluation:
        metrics = self._calculate_team_metrics(team_id, period_start, period_end, events)
        score = self.calculate_team_score(team_id, metrics)
        grade = self.grade_score(score)
        recommendations = self._generate_team_recommendations(team_id, metrics)

        return TeamEvaluation(
            team_id=team_id,
            period_start=period_start,
            period_end=period_end,
            metrics=metrics,
            score=score,
            grade=grade,
            recommendations=recommendations
        )

    def _calculate_agent_metrics(
        self,
        agent_id: str,
        period_start: datetime,
        period_end: datetime,
        events: List[Dict[str, Any]]
    ) -> Dict[str, AgentMetric]:
        metrics = {}

        for key, template in AGENT_METRIC_DEFINITIONS.items():
            metrics[key] = AgentMetric(
                metric_id=template.metric_id,
                name=template.name,
                description=template.description,
                unit=template.unit
            )

        completed_tasks = 0
        task_times = []
        review_times = []
        blocker_times = []
        response_times = []
        meeting_count = 0
        total_meetings = 0

        period_events = [
            e for e in events
            if e.get("agent_id") == agent_id
            and period_start <= e.get("timestamp", datetime.min)
            <= period_end
        ]

        for event in period_events:
            event_type = event.get("type")

            if event_type == "ticket_completed":
                completed_tasks += 1
                start = event.get("started_at")
                end = event.get("completed_at")
                if start and end:
                    duration = (end - start).total_seconds() / 3600
                    task_times.append(duration)

            elif event_type == "code_review_completed":
                start = event.get("started_at")
                end = event.get("completed_at")
                if start and end:
                    duration = (end - start).total_seconds() / 3600
                    review_times.append(duration)

            elif event_type == "blocker_resolved":
                start = event.get("reported_at")
                end = event.get("resolved_at")
                if start and end:
                    duration = (end - start).total_seconds() / 3600
                    blocker_times.append(duration)

            elif event_type == "communication_received":
                start = event.get("received_at")
                end = event.get("responded_at")
                if start and end:
                    duration = (end - start).total_seconds() / 3600
                    response_times.append(duration)

            elif event_type == "meeting_participated":
                meeting_count += 1
                total_meetings += 1

            elif event_type == "meeting_scheduled":
                total_meetings += 1

        if completed_tasks > 0:
            metrics[AgentMetrics.TASKS_COMPLETED].values.append(
                MetricValue(value=float(completed_tasks))
            )

        if task_times:
            avg_cycle_time = sum(task_times) / len(task_times)
            metrics[AgentMetrics.TICKET_CYCLE_TIME].values.append(
                MetricValue(value=avg_cycle_time))

        if review_times:
            avg_review_time = sum(review_times) / len(review_times)
            metrics[AgentMetrics.CODE_REVIEW_TURNAROUND].values.append(
                MetricValue(value=avg_review_time))

        if blocker_times:
            avg_blocker_time = sum(blocker_times) / len(blocker_times)
            metrics[AgentMetrics.BLOCKER_RESOLUTION_TIME].values.append(
                MetricValue(value=avg_blocker_time))

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            metrics[AgentMetrics.COMMUNICATION_RESPONSE_TIME].values.append(
                MetricValue(value=avg_response_time))

        if total_meetings > 0:
            participation_rate = (meeting_count / total_meetings) * 100
            metrics[AgentMetrics.MEETING_PARTICIPATION_RATE].values.append(
                MetricValue(value=participation_rate))

        if completed_tasks > 0:
            days = (period_end - period_start).days or 1
            velocity = completed_tasks / days
            metrics[AgentMetrics.TASK_VELOCITY].values.append(
                MetricValue(value=velocity))

        return metrics

    def _calculate_team_metrics(
        self,
        team_id: str,
        period_start: datetime,
        period_end: datetime,
        events: List[Dict[str, Any]]
    ) -> Dict[str, TeamMetric]:
        metrics = {}

        for key, template in TEAM_METRIC_DEFINITIONS.items():
            metrics[key] = TeamMetric(
                metric_id=template.metric_id,
                name=template.name,
                description=template.description,
                unit=template.unit
            )

        story_points = 0
        backlog_items = 0
        cleared_items = 0
        escalations = 0
        meeting_effectiveness_ratings = []
        bug_count = 0
        ticket_count = 0

        period_events = [
            e for e in events
            if e.get("team_id") == team_id
            and period_start <= e.get("timestamp", datetime.min)
            <= period_end
        ]

        for event in period_events:
            event_type = event.get("type")

            if event_type == "sprint_completed":
                story_points += event.get("story_points", 0)

            elif event_type == "backlog_item_cleared":
                cleared_items += 1

            elif event_type == "backlog_item_added":
                backlog_items += 1

            elif event_type == "blocker_escalated":
                escalations += 1

            elif event_type == "meeting_effectiveness_rated":
                rating = event.get("rating", 0)
                if rating > 0:
                    meeting_effectiveness_ratings.append(rating)

            elif event_type == "ticket_completed":
                ticket_count += 1
                if event.get("has_bugs", False):
                    bug_count += 1

        if story_points > 0:
            metrics[TeamMetrics.SPRINT_VELOCITY].values.append(
                MetricValue(value=float(story_points)))

        if backlog_items > 0:
            clearance_rate = (cleared_items / backlog_items) * 100
            metrics[TeamMetrics.BACKLOG_CLEARANCE_RATE].values.append(
                MetricValue(value=clearance_rate))

        if escalations > 0:
            metrics[TeamMetrics.BLOCKER_ESCALATION_FREQUENCY].values.append(
                MetricValue(value=float(escalations)))

        if meeting_effectiveness_ratings:
            avg_rating = sum(meeting_effectiveness_ratings) / len(meeting_effectiveness_ratings)
            metrics[TeamMetrics.MEETING_EFFECTIVENESS].values.append(
                MetricValue(value=avg_rating))

        if ticket_count > 0:
            quality_score = ((ticket_count - bug_count) / ticket_count) * 100
            metrics[TeamMetrics.QUALITY_SCORE].values.append(
                MetricValue(value=quality_score))

        return metrics

    def _generate_agent_recommendations(
        self,
        agent_id: str,
        metrics: Dict[str, AgentMetric]
    ) -> List[str]:
        recommendations = []

        cycle_time = metrics.get(AgentMetrics.TICKET_CYCLE_TIME)
        if cycle_time:
            current = cycle_time.get_current()
            if current and current > 48:
                recommendations.append(
                    "Consider breaking down tasks into smaller pieces to reduce cycle time"
                )

        review_time = metrics.get(AgentMetrics.CODE_REVIEW_TURNAROUND)
        if review_time:
            current = review_time.get_current()
            if current and current > 24:
                recommendations.append(
                    "Prioritize code reviews earlier in the day to reduce turnaround time"
                )

        participation = metrics.get(AgentMetrics.MEETING_PARTICIPATION_RATE)
        if participation:
            current = participation.get_current()
            if current and current < 80:
                recommendations.append(
                    "Increase meeting participation to improve team collaboration"
                )

        velocity = metrics.get(AgentMetrics.TASK_VELOCITY)
        if velocity:
            trend = velocity.get_trend()
            if trend and trend < 0:
                recommendations.append(
                    "Task velocity is declining. Consider reviewing workload balance"
                )

        return recommendations

    def _generate_team_recommendations(
        self,
        team_id: str,
        metrics: Dict[str, TeamMetric]
    ) -> List[str]:
        recommendations = []

        velocity = metrics.get(TeamMetrics.SPRINT_VELOCITY)
        if velocity:
            current = velocity.get_current()
            trend = velocity.get_trend()
            if current and current < 20:
                recommendations.append(
                    "Sprint velocity is low. Consider refining story point estimation"
                )
            elif trend and trend < -5:
                recommendations.append(
                    "Velocity is declining. Review for blockers or capacity issues"
                )

        clearance = metrics.get(TeamMetrics.BACKLOG_CLEARANCE_RATE)
        if clearance:
            current = clearance.get_current()
            if current and current < 50:
                recommendations.append(
                    "Low backlog clearance. Prioritize backlog refinement sessions"
                )

        escalations = metrics.get(TeamMetrics.BLOCKER_ESCALATION_FREQUENCY)
        if escalations:
            current = escalations.get_current()
            if current and current > 3:
                recommendations.append(
                    "High blocker escalation frequency. Improve early detection"
                )

        quality = metrics.get(TeamMetrics.QUALITY_SCORE)
        if quality:
            current = quality.get_current()
            if current and current < 80:
                recommendations.append(
                    "Quality score needs improvement. Increase testing coverage"
                )

        return recommendations

    def set_goal(
        self,
        entity_id: str,
        metric_id: str,
        target_value: float
    ) -> None:
        if entity_id not in self._goals:
            self._goals[entity_id] = []

        goal = GoalTarget(
            metric_id=metric_id,
            target_value=target_value
        )
        self._goals[entity_id].append(goal)

    def check_goals(
        self,
        entity_id: str,
        metrics: Dict[str, AgentMetric] | Dict[str, TeamMetric]
    ) -> List[GoalTarget]:
        if entity_id not in self._goals:
            return []

        achieved_goals = []
        for goal in self._goals[entity_id]:
            if goal.metric_id in metrics:
                metric = metrics[goal.metric_id]
                goal.current_value = metric.get_current() or 0.0
                goal.check_achievement()
                achieved_goals.append(goal)

        return achieved_goals

    def get_historical_trend(
        self,
        metrics: Dict[str, AgentMetric] | Dict[str, TeamMetric],
        metric_id: str,
        days: int = 30
    ) -> Optional[float]:
        if metric_id not in metrics:
            return None

        metric = metrics[metric_id]
        return metric.get_trend(days)

    def compare_to_benchmark(
        self,
        metrics: Dict[str, AgentMetric] | Dict[str, TeamMetric],
        metric_id: str,
        benchmark: float
    ) -> Optional[float]:
        if metric_id not in metrics:
            return None

        metric = metrics[metric_id]
        current = metric.get_current()

        if current is None:
            return None

        return current - benchmark