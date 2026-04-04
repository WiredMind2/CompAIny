from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field

from .enums import TicketStatus

if TYPE_CHECKING:
    from .ticket import Ticket


@dataclass
class Swimlane:
    team_id: str
    tickets: List[str] = field(default_factory=list)


@dataclass
class TicketBoard:
    id: str
    name: str
    team_id: Optional[str] = None
    swimlanes: Dict[str, Swimlane] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_swimlane(self, team_id: str) -> Swimlane:
        if team_id not in self.swimlanes:
            self.swimlanes[team_id] = Swimlane(team_id=team_id)
            self.updated_at = datetime.utcnow()
        return self.swimlanes[team_id]

    def remove_swimlane(self, team_id: str) -> bool:
        if team_id in self.swimlanes:
            del self.swimlanes[team_id]
            self.updated_at = datetime.utcnow()
            return True
        return False

    def get_swimlane(self, team_id: str) -> Optional[Swimlane]:
        return self.swimlanes.get(team_id)

    def add_ticket_to_swimlane(self, team_id: str, ticket_id: str) -> None:
        if team_id not in self.swimlanes:
            self.add_swimlane(team_id)
        if ticket_id not in self.swimlanes[team_id].tickets:
            self.swimlanes[team_id].tickets.append(ticket_id)
            self.updated_at = datetime.utcnow()

    def remove_ticket_from_swimlane(self, team_id: str, ticket_id: str) -> bool:
        if team_id in self.swimlanes and ticket_id in self.swimlanes[team_id].tickets:
            self.swimlanes[team_id].tickets.remove(ticket_id)
            self.updated_at = datetime.utcnow()
            return True
        return False

    def get_tickets_by_status(self, tickets: Dict[str, "Ticket"]) -> Dict[TicketStatus, List[str]]:
        result = {status: [] for status in TicketStatus}
        for ticket in tickets.values():
            result[ticket.status].append(ticket.id)
        return result

    def get_swimlane_tickets(self, team_id: str, tickets: Dict[str, "Ticket"]) -> Dict[TicketStatus, List[str]]:
        if team_id not in self.swimlanes:
            return {status: [] for status in TicketStatus}
        
        team_ticket_ids = self.swimlanes[team_id].tickets
        result = {status: [] for status in TicketStatus}
        for ticket_id in team_ticket_ids:
            if ticket_id in tickets:
                result[tickets[ticket_id].status].append(ticket_id)
        return result