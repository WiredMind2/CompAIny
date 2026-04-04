from typing import Dict, List, Optional
from .models import Agent, Team, Ticket, Meeting


class CompanyStore:
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._teams: Dict[str, Team] = {}
        self._tickets: Dict[str, Ticket] = {}
        self._meetings: Dict[str, Meeting] = {}

    def add_agent(self, agent: Agent) -> None:
        self._agents[agent.id] = agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self._agents.get(agent_id)

    def list_agents(self) -> List[Agent]:
        return list(self._agents.values())

    def list_agents_by_team(self, team_id: str) -> List[Agent]:
        return [a for a in self._agents.values() if a.team_id == team_id]

    def add_team(self, team: Team) -> None:
        self._teams[team.id] = team

    def get_team(self, team_id: str) -> Optional[Team]:
        return self._teams.get(team_id)

    def list_teams(self) -> List[Team]:
        return list(self._teams.values())

    def add_ticket(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return self._tickets.get(ticket_id)

    def list_tickets(self) -> List[Ticket]:
        return list(self._tickets.values())

    def list_tickets_by_team(self, team_id: str) -> List[Ticket]:
        return [t for t in self._tickets.values()]

    def list_tickets_by_assignee(self, assignee_id: str) -> List[Ticket]:
        return [t for t in self._tickets.values() if t.assignee_id == assignee_id]

    def add_meeting(self, meeting: Meeting) -> None:
        self._meetings[meeting.id] = meeting

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        return self._meetings.get(meeting_id)

    def list_meetings(self) -> List[Meeting]:
        return list(self._meetings.values())

    def list_meetings_by_team(self, team_id: str) -> List[Meeting]:
        return [m for m in self._meetings.values() if m.team_id == team_id]


_store = CompanyStore()


def get_store() -> CompanyStore:
    return _store


def reset_store() -> None:
    global _store
    _store = CompanyStore()