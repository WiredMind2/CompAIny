from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.company import Company


class AutomationRules:
    def __init__(self, company: "Company", workflow_engine: "WorkflowEngine"):
        self.company = company
        self.workflow_engine = workflow_engine

    def on_ticket_completed(self, agent_id: str, ticket_id: Optional[str], team_id: Optional[str]) -> Optional[str]:
        if not team_id:
            return None
        
        next_ticket = self._find_next_available_ticket(team_id)
        if next_ticket:
            self.company.assign_ticket(next_ticket.id, agent_id)
            return next_ticket.id
        
        team = self.company.get_team(team_id)
        if team:
            self.workflow_engine.notify_team_lead(
                team.leader_id,
                f"No more tickets available for team {team.name}"
            )
        return None

    def _find_next_available_ticket(self, team_id: str):
        from ..models.enums import TicketStatus
        for ticket in self.company.tickets.values():
            if ticket.team_id == team_id and ticket.status in [
                TicketStatus.BACKLOG, 
                TicketStatus.TODO
            ]:
                return ticket
        return None

    def on_team_completed(self, team_id: Optional[str], sprint_ended: bool = False) -> Optional[str]:
        from ..models.meeting import MeetingType
        team = self.company.get_team(team_id)
        if not team:
            return None
        
        meeting_type = MeetingType.RETROSPECTIVE if sprint_ended else MeetingType.STANDUP
        return self.company.create_meeting(meeting_type, team_id, team.leader_id)

    def on_ticket_blocked(self, ticket_id: Optional[str], team_id: Optional[str], reason: str) -> None:
        if not team_id:
            return
        team = self.company.get_team(team_id)
        if team:
            self.workflow_engine.notify_team_lead(
                team.leader_id,
                f"Blocker on ticket {ticket_id}: {reason}"
            )

    def on_review_completed(self, ticket_id: Optional[str], team_id: Optional[str]) -> Optional[str]:
        if not team_id:
            return None
        from ..models.meeting import MeetingType
        team = self.company.get_team(team_id)
        if not team:
            return None
        return self.company.create_meeting(MeetingType.REVIEW, team_id, team.leader_id)

    def on_ticket_accepted(self, ticket_id: Optional[str], team_id: Optional[str]) -> Optional[str]:
        if not team_id:
            return None
        from ..models.meeting import MeetingType
        team = self.company.get_team(team_id)
        if not team:
            return None
        return self.company.create_meeting(MeetingType.PLANNING, team_id, team.leader_id)