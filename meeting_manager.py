from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
from meeting import Meeting, MeetingType, MeetingStatus, MeetingReport, DailyStandup, SprintPlanning, Retrospective
from enum import Enum


class StandupProgress(Enum):
    COMPLETED = "completed"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    NOT_STARTED = "not_started"


@dataclass
class StandupUpdate:
    agent_id: str
    agent_name: str
    progress: StandupProgress
    completed_tasks: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    blockers: List[str] = field(default_factory=list)
    plan_for_today: List[str] = field(default_factory=list)


class MeetingManager:
    def __init__(self):
        self.meetings: Dict[str, Meeting] = {}
        self.team_leaders: Dict[str, str] = {}
        self.team_hierarchy: Dict[str, str] = {}
        self._get_team_leader: Optional[Callable[[str], Optional[str]]] = None
        self._get_boss: Optional[Callable[[str], Optional[str]]] = None
        self._get_team_members: Optional[Callable[[str], List[str]]] = None
        self._get_agent_name: Optional[Callable[[str], str]] = None

    def set_hierarchy_callbacks(
        self,
        get_team_leader: Callable[[str], Optional[str]],
        get_boss: Callable[[str], Optional[str]],
        get_team_members: Callable[[str], List[str]],
        get_agent_name: Callable[[str], str]
    ):
        self._get_team_leader = get_team_leader
        self._get_boss = get_boss
        self._get_team_members = get_team_members
        self._get_agent_name = get_agent_name

    def set_team_leader(self, team_id: str, leader_id: str) -> None:
        self.team_leaders[team_id] = leader_id

    def set_team_hierarchy(self, team_id: str, parent_team_id: str) -> None:
        self.team_hierarchy[team_id] = parent_team_id

    def create_standup(self, team_id: str, created_by: str, sprint_id: Optional[str] = None) -> DailyStandup:
        standup = DailyStandup(team_id, created_by, sprint_id)
        self.meetings[standup.meeting_id] = standup

        if self._get_team_members:
            members = self._get_team_members(team_id)
            for member in members:
                standup.add_participant(member)

        return standup

    def create_sprint_planning(self, team_id: str, created_by: str, sprint_id: str) -> SprintPlanning:
        planning = SprintPlanning(team_id, created_by, sprint_id)
        self.meetings[planning.meeting_id] = planning

        if self._get_team_members:
            members = self._get_team_members(team_id)
            for member in members:
                planning.add_participant(member)

        return planning

    def create_retrospective(self, team_id: str, created_by: str, sprint_id: str) -> Retrospective:
        retro = Retrospective(team_id, created_by, sprint_id)
        self.meetings[retro.meeting_id] = retro

        if self._get_team_members:
            members = self._get_team_members(team_id)
            for member in members:
                retro.add_participant(member)

        return retro

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        return self.meetings.get(meeting_id)

    def start_standup_report(
        self,
        meeting_id: str,
        agent_id: str,
        agent_name: str,
        progress: StandupProgress,
        completed_tasks: List[str] = None,
        current_task: Optional[str] = None,
        blockers: List[str] = None,
        plan_for_today: List[str] = None
    ) -> Optional[MeetingReport]:
        meeting = self.meetings.get(meeting_id)
        if not meeting or meeting.meeting_type != MeetingType.DAILY_STANDUP:
            return None

        details = {
            "progress": progress.value,
            "completed_tasks": completed_tasks or [],
            "current_task": current_task,
            "blockers": blockers or [],
            "plan_for_today": plan_for_today or []
        }

        report = meeting.create_report(
            creator_id=agent_id,
            creator_name=agent_name,
            summary=self._generate_standup_summary(progress, current_task, completed_tasks, blockers),
            details=details
        )

        return report

    def _generate_standup_summary(
        self,
        progress: StandupProgress,
        current_task: Optional[str],
        completed: List[str],
        blockers: List[str]
    ) -> str:
        if blockers:
            return f"BLOCKED: {', '.join(blockers)}"
        elif progress == StandupProgress.COMPLETED:
            return f"Completed: {', '.join(completed) if completed else 'All tasks done'}"
        elif current_task:
            return f"Working on: {current_task}"
        return "No updates"

    def start_planning_report(
        self,
        meeting_id: str,
        agent_id: str,
        agent_name: str,
        tickets: List[Dict[str, Any]],
        subtask_breakdown: Dict[str, List[str]] = None,
        complexity_estimates: Dict[str, int] = None,
        recruitment_decisions: List[str] = None,
        accepted_tickets: List[str] = None,
        rejected_tickets: List[str] = None
    ) -> Optional[MeetingReport]:
        meeting = self.meetings.get(meeting_id)
        if not meeting or meeting.meeting_type != MeetingType.SPRINT_PLANNING:
            return None

        details = {
            "tickets": tickets,
            "subtask_breakdown": subtask_breakdown or {},
            "complexity_estimates": complexity_estimates or {},
            "recruitment_decisions": recruitment_decisions or [],
            "accepted_tickets": accepted_tickets or [],
            "rejected_tickets": rejected_tickets or []
        }

        accepted = accepted_tickets or []
        rejected = rejected_tickets or []
        summary = f"Planning: {len(accepted)} accepted, {len(rejected)} rejected"
        if recruitment_decisions:
            summary += f", {len(recruitment_decisions)} recruitment decisions"

        report = meeting.create_report(
            creator_id=agent_id,
            creator_name=agent_name,
            summary=summary,
            details=details,
            decisions=[f"Accepted: {t}" for t in accepted] + [f"Rejected: {t}" for t in rejected]
        )

        return report

    def start_retrospective_report(
        self,
        meeting_id: str,
        agent_id: str,
        agent_name: str,
        what_went_well: List[str] = None,
        what_could_improve: List[str] = None,
        action_items: List[Dict[str, Any]] = None
    ) -> Optional[MeetingReport]:
        meeting = self.meetings.get(meeting_id)
        if not meeting or meeting.meeting_type != MeetingType.RETROSPECTIVE:
            return None

        details = {
            "what_went_well": what_went_well or [],
            "what_could_improve": what_could_improve or [],
            "action_items": action_items or []
        }

        report = meeting.create_report(
            creator_id=agent_id,
            creator_name=agent_name,
            summary=f"Retro: {len(what_went_well or [])} positives, {len(what_could_improve or [])} improvements",
            details=details,
            action_items=action_items or []
        )

        return report

    def propagate_report_up_hierarchy(self, report: MeetingReport) -> List[MeetingReport]:
        propagated = []
        if not self._get_boss:
            return propagated

        creator_team_id = self._find_team_for_agent(report.creator_id)
        if not creator_team_id:
            return propagated

        parent_team_id = self.team_hierarchy.get(creator_team_id)
        if not parent_team_id:
            return propagated

        parent_leader = self.team_leaders.get(parent_team_id)
        if not parent_leader:
            return propagated

        parent_report = MeetingReport(
            report_id=str(uuid.uuid4()),
            meeting_id=report.meeting_id,
            meeting_type=report.meeting_type,
            created_at=datetime.now(),
            creator_id=parent_leader,
            creator_name=self._get_agent_name(parent_leader) if self._get_agent_name else parent_leader,
            summary=f"[Escalated] {report.summary}",
            details=report.details,
            action_items=report.action_items,
            decisions=report.decisions,
            parent_report_id=report.report_id
        )
        propagated.append(parent_report)
        return propagated

    def _find_team_for_agent(self, agent_id: str) -> Optional[str]:
        for team_id, leader_id in self.team_leaders.items():
            if leader_id == agent_id:
                return team_id

        if self._get_team_members:
            for team_id, members in [(tid, self._get_team_members(tid)) for tid in self.team_leaders]:
                if agent_id in members:
                    return team_id

        return None

    def can_control_speaker(self, meeting_id: str, agent_id: str) -> bool:
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return False

        team_leader = self.team_leaders.get(meeting.team_id)
        if team_leader and team_leader == agent_id:
            return True

        if meeting.current_speaker and meeting.current_speaker == agent_id:
            return True

        return False

    def control_speaker(self, meeting_id: str, controller_id: str, target_speaker: Optional[str]) -> bool:
        if not self.can_control_speaker(meeting_id, controller_id):
            return False

        meeting = self.meetings.get(meeting_id)
        if meeting:
            meeting.current_speaker = target_speaker
            return True

        return False

    def get_team_meetings(self, team_id: str, meeting_type: Optional[MeetingType] = None) -> List[Meeting]:
        meetings = []
        for meeting in self.meetings.values():
            if meeting.team_id != team_id:
                continue
            if meeting_type and meeting.meeting_type != meeting_type:
                continue
            meetings.append(meeting)
        return meetings

    def get_upcoming_meetings(self, team_id: str) -> List[Meeting]:
        upcoming = []
        for meeting in self.meetings.values():
            if meeting.team_id != team_id:
                continue
            if meeting.status in [MeetingStatus.SCHEDULED, MeetingStatus.IN_PROGRESS]:
                upcoming.append(meeting)
        return upcoming


import uuid