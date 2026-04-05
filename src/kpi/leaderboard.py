from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from .evaluator import AgentEvaluation, TeamEvaluation, Evaluator
from .metrics import AgentMetrics, TeamMetrics, AGENT_METRIC_DEFINITIONS, TEAM_METRIC_DEFINITIONS


@dataclass
class AgentRanking:
    agent_id: str
    rank: int
    score: float
    previous_rank: Optional[int] = None
    rank_change: int = 0

    def __post_init__(self):
        if self.previous_rank is not None:
            self.rank_change = self.previous_rank - self.rank


@dataclass
class TeamRanking:
    team_id: str
    rank: int
    score: float
    previous_rank: Optional[int] = None
    rank_change: int = 0

    def __post_init__(self):
        if self.previous_rank is not None:
            self.rank_change = self.previous_rank - self.rank


@dataclass
class TrendAnalysis:
    metric_id: str
    direction: str
    change_percentage: float
    significance: str


@dataclass
class MostImproved:
    entity_id: str
    improvement_score: float
    category: str


class Leaderboard:
    def __init__(self):
        self._agent_rankings: Dict[str, AgentRanking] = {}
        self._team_rankings: Dict[str, TeamRanking] = {}
        self._historical_agent_scores = {}
        self._historical_team_scores = {}
        self._evaluator = Evaluator()

    def rank_agents(
        self,
        evaluations: List[AgentEvaluation],
        top_n: int = 10
    ) -> List[AgentRanking]:
        sorted_evals = sorted(
            evaluations,
            key=lambda e: e.score,
            reverse=True
        )

        rankings = []
        for i, evaluation in enumerate(sorted_evals[:top_n], 1):
            previous_rank = None
            if evaluation.agent_id in self._agent_rankings:
                previous_rank = self._agent_rankings[evaluation.agent_id].rank

            ranking = AgentRanking(
                agent_id=evaluation.agent_id,
                rank=i,
                score=evaluation.score,
                previous_rank=previous_rank
            )
            rankings.append(ranking)
            self._agent_rankings[evaluation.agent_id] = ranking

            if evaluation.agent_id not in self._historical_agent_scores:
                self._historical_agent_scores[evaluation.agent_id] = []
            self._historical_agent_scores[evaluation.agent_id].append(
                (datetime.utcnow(), evaluation.score)
            )

        return rankings

    def rank_teams(
        self,
        evaluations: List[TeamEvaluation],
        top_n: int = 10
    ) -> List[TeamRanking]:
        sorted_evals = sorted(
            evaluations,
            key=lambda e: e.score,
            reverse=True
        )

        rankings = []
        for i, evaluation in enumerate(sorted_evals[:top_n], 1):
            previous_rank = None
            if evaluation.team_id in self._team_rankings:
                previous_rank = self._team_rankings[evaluation.team_id].rank

            ranking = TeamRanking(
                team_id=evaluation.team_id,
                rank=i,
                score=evaluation.score,
                previous_rank=previous_rank
            )
            rankings.append(ranking)
            self._team_rankings[evaluation.team_id] = ranking

            if evaluation.team_id not in self._historical_team_scores:
                self._historical_team_scores[evaluation.team_id] = []
            self._historical_team_scores[evaluation.team_id].append(
                (datetime.utcnow(), evaluation.score)
            )

        return rankings

    def get_top_performers(
        self,
        metric_id: str,
        evaluations: List[AgentEvaluation],
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        metric_scores = []

        for evaluation in evaluations:
            if metric_id in evaluation.metrics:
                metric = evaluation.metrics[metric_id]
                current = metric.get_current()
                if current is not None:
                    metric_scores.append((evaluation.agent_id, current))

        metric_scores.sort(key=lambda x: x[1], reverse=True)
        return metric_scores[:top_n]

    def get_most_improved_agents(
        self,
        current_evaluations: List[AgentEvaluation],
        days: int = 30
    ) -> List[MostImproved]:
        improvements = []

        cutoff = datetime.utcnow().timestamp() - (days * 86400)

        for evaluation in current_evaluations:
            agent_id = evaluation.agent_id

            if agent_id not in self._historical_agent_scores:
                continue

            history = self._historical_agent_scores[agent_id]
            old_scores = [
                score for timestamp, score in history
                if timestamp.timestamp() < cutoff
            ]
            new_scores = [
                score for timestamp, score in history
                if timestamp.timestamp() >= cutoff
            ]

            if not old_scores or not new_scores:
                continue

            old_avg = sum(old_scores) / len(old_scores)
            new_avg = sum(new_scores) / len(new_scores)
            improvement = new_avg - old_avg

            if improvement > 0:
                improvements.append(MostImproved(
                    entity_id=agent_id,
                    improvement_score=improvement,
                    category="overall"
                ))

        improvements.sort(key=lambda x: x.improvement_score, reverse=True)
        return improvements[:5]

    def get_most_improved_teams(
        self,
        current_evaluations: List[TeamEvaluation],
        days: int = 30
    ) -> List[MostImproved]:
        improvements = []

        cutoff = datetime.utcnow().timestamp() - (days * 86400)

        for evaluation in current_evaluations:
            team_id = evaluation.team_id

            if team_id not in self._historical_team_scores:
                continue

            history = self._historical_team_scores[team_id]
            old_scores = [
                score for timestamp, score in history
                if timestamp.timestamp() < cutoff
            ]
            new_scores = [
                score for timestamp, score in history
                if timestamp.timestamp() >= cutoff
            ]

            if not old_scores or not new_scores:
                continue

            old_avg = sum(old_scores) / len(old_scores)
            new_avg = sum(new_scores) / len(new_scores)
            improvement = new_avg - old_avg

            if improvement > 0:
                improvements.append(MostImproved(
                    entity_id=team_id,
                    improvement_score=improvement,
                    category="overall"
                ))

        improvements.sort(key=lambda x: x.improvement_score, reverse=True)
        return improvements[:5]

    def analyze_trends(
        self,
        evaluations: List[AgentEvaluation] | List[TeamEvaluation],
        metric_ids: List[str],
        days: int = 30
    ) -> List[TrendAnalysis]:
        trends = []

        for evaluation in evaluations:
            metrics = evaluation.metrics

            for metric_id in metric_ids:
                if metric_id not in metrics:
                    continue

                metric = metrics[metric_id]
                trend = metric.get_trend(days)

                if trend is None:
                    continue

                current = metric.get_current()
                avg = metric.get_average(days)

                if avg and avg > 0:
                    change_pct = (trend / avg) * 100

                    if abs(change_pct) < 5:
                        significance = "stable"
                    elif abs(change_pct) < 15:
                        significance = "minor"
                    elif abs(change_pct) < 30:
                        significance = "moderate"
                    else:
                        significance = "significant"

                    direction = "increasing" if trend > 0 else "decreasing"

                    if metric_id in [
                        AgentMetrics.TICKET_CYCLE_TIME,
                        AgentMetrics.CODE_REVIEW_TURNAROUND,
                        AgentMetrics.BLOCKER_RESOLUTION_TIME,
                        AgentMetrics.COMMUNICATION_RESPONSE_TIME,
                    ]:
                        direction = "improving" if trend < 0 else "declining"

                    trends.append(TrendAnalysis(
                        metric_id=metric_id,
                        direction=direction,
                        change_percentage=change_pct,
                        significance=significance
                    ))

        return trends

    def get_agent_position(
        self,
        agent_id: str,
        metric_id: str,
        evaluations: List[AgentEvaluation]
    ) -> Optional[int]:
        metric_scores = []

        for evaluation in evaluations:
            if metric_id in evaluation.metrics:
                metric = evaluation.metrics[metric_id]
                current = metric.get_current()
                if current is not None:
                    metric_scores.append((evaluation.agent_id, current))

        metric_scores.sort(key=lambda x: x[1], reverse=True)

        for i, (aid, _) in enumerate(metric_scores, 1):
            if aid == agent_id:
                return i

        return None

    def get_team_position(
        self,
        team_id: str,
        metric_id: str,
        evaluations: List[TeamEvaluation]
    ) -> Optional[int]:
        metric_scores = []

        for evaluation in evaluations:
            if metric_id in evaluation.metrics:
                metric = evaluation.metrics[metric_id]
                current = metric.get_current()
                if current is not None:
                    metric_scores.append((evaluation.team_id, current))

        metric_scores.sort(key=lambda x: x[1], reverse=True)

        for i, (tid, _) in enumerate(metric_scores, 1):
            if tid == team_id:
                return i

        return None

    def compare_agents(
        self,
        agent_id_1: str,
        agent_id_2: str,
        evaluations: List[AgentEvaluation]
    ) -> Dict[str, Any]:
        eval_1 = None
        eval_2 = None

        for e in evaluations:
            if e.agent_id == agent_id_1:
                eval_1 = e
            elif e.agent_id == agent_id_2:
                eval_2 = e

        if not eval_1 or not eval_2:
            return {"error": "One or both agents not found"}

        comparison = {
            "agent_1": agent_id_1,
            "agent_2": agent_id_2,
            "overall_score_1": eval_1.score,
            "overall_score_2": eval_2.score,
            "better_performer": agent_id_1 if eval_1.score > eval_2.score else agent_id_2,
            "metric_comparisons": {}
        }

        for metric_id in AGENT_METRIC_DEFINITIONS:
            if metric_id in eval_1.metrics and metric_id in eval_2.metrics:
                val_1 = eval_1.metrics[metric_id].get_current()
                val_2 = eval_2.metrics[metric_id].get_current()

                comparison["metric_comparisons"][metric_id] = {
                    "agent_1_value": val_1,
                    "agent_2_value": val_2,
                    "winner": agent_id_1 if val_1 and val_2 and val_1 > val_2 else agent_id_2
                }

        return comparison

    def compare_teams(
        self,
        team_id_1: str,
        team_id_2: str,
        evaluations: List[TeamEvaluation]
    ) -> Dict[str, Any]:
        eval_1 = None
        eval_2 = None

        for e in evaluations:
            if e.team_id == team_id_1:
                eval_1 = e
            elif e.team_id == team_id_2:
                eval_2 = e

        if not eval_1 or not eval_2:
            return {"error": "One or both teams not found"}

        comparison = {
            "team_1": team_id_1,
            "team_2": team_id_2,
            "overall_score_1": eval_1.score,
            "overall_score_2": eval_2.score,
            "better_performer": team_id_1 if eval_1.score > eval_2.score else team_id_2,
            "metric_comparisons": {}
        }

        for metric_id in TEAM_METRIC_DEFINITIONS:
            if metric_id in eval_1.metrics and metric_id in eval_2.metrics:
                val_1 = eval_1.metrics[metric_id].get_current()
                val_2 = eval_2.metrics[metric_id].get_current()

                comparison["metric_comparisons"][metric_id] = {
                    "team_1_value": val_1,
                    "team_2_value": val_2,
                    "winner": team_id_1 if val_1 and val_2 and val_1 > val_2 else team_id_2
                }

        return comparison

    def export_rankings_json(
        self,
        agent_rankings: List[AgentRanking],
        team_rankings: List[TeamRanking]
    ) -> Dict[str, Any]:
        return {
            "agent_rankings": [
                {
                    "agent_id": r.agent_id,
                    "rank": r.rank,
                    "score": r.score,
                    "rank_change": r.rank_change
                }
                for r in agent_rankings
            ],
            "team_rankings": [
                {
                    "team_id": r.team_id,
                    "rank": r.rank,
                    "score": r.score,
                    "rank_change": r.rank_change
                }
                for r in team_rankings
            ],
            "exported_at": datetime.utcnow().isoformat()
        }