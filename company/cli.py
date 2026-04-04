from __future__ import annotations
import argparse
import json
import sys
from typing import Optional
from enum import Enum
from company.models import (
    Agent,
    Team,
    Ticket,
    Meeting,
    Role,
    Level,
    TeamType,
    TicketStatus,
    TicketPriority,
    MeetingType,
)


class InMemoryStore:
    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.teams: dict[str, Team] = {}
        self.tickets: dict[str, Ticket] = {}
        self.meetings: dict[str, Meeting] = {}

    def add_agent(self, agent: Agent) -> None:
        self.agents[agent.id] = agent

    def add_team(self, team: Team) -> None:
        self.teams[team.id] = team

    def add_ticket(self, ticket: Ticket) -> None:
        self.tickets[ticket.id] = ticket

    def add_meeting(self, meeting: Meeting) -> None:
        self.meetings[meeting.id] = meeting


store = InMemoryStore()


def create_agent(
    agent_id: str,
    role: Role,
    level: Level,
    team_id: Optional[str] = None,
    boss_id: Optional[str] = None,
) -> Agent:
    agent = Agent(id=agent_id, role=role, level=level, team_id=team_id, boss_id=boss_id)
    store.add_agent(agent)
    return agent


def create_team(team_id: str, team_type: TeamType, leader_id: str) -> Team:
    team = Team(id=team_id, type=team_type, leader_id=leader_id)
    store.add_team(team)
    return team


def create_ticket(ticket_id: str, priority: TicketPriority = TicketPriority.MEDIUM) -> Ticket:
    ticket = Ticket(id=ticket_id, priority=priority)
    store.add_ticket(ticket)
    return ticket


def assign_ticket(ticket_id: str, agent_id: str) -> Ticket:
    ticket = store.tickets[ticket_id]
    ticket.assignee_id = agent_id
    ticket.status = TicketStatus.TODO
    return ticket


def update_ticket_status(ticket_id: str, status: TicketStatus) -> Ticket:
    ticket = store.tickets[ticket_id]
    ticket.status = status
    return ticket


def create_meeting(meeting_id: str, meeting_type: MeetingType, leader_id: str) -> Meeting:
    meeting = Meeting(id=meeting_id, type=meeting_type, leader_id=leader_id)
    store.add_meeting(meeting)
    return meeting


def attend_meeting(meeting_id: str, agent_id: str) -> Meeting:
    meeting = store.meetings[meeting_id]
    if agent_id not in meeting.participant_ids:
        meeting.participant_ids.append(agent_id)
    return meeting


def add_meeting_report(meeting_id: str, author_id: str, content: str) -> Meeting:
    meeting = store.meetings[meeting_id]
    meeting.add_report(author_id, content)
    return meeting


def list_teams() -> list[Team]:
    return list(store.teams.values())


def list_tickets(status: Optional[TicketStatus] = None) -> list[Ticket]:
    if status:
        return [t for t in store.tickets.values() if t.status == status]
    return list(store.tickets.values())


def list_meetings() -> list[Meeting]:
    return list(store.meetings.values())


def get_progress() -> dict:
    all_tickets = list(store.tickets.values())
    total = len(all_tickets)
    done = sum(1 for t in all_tickets if t.status == TicketStatus.DONE)
    in_progress = sum(1 for t in all_tickets if t.status == TicketStatus.IN_PROGRESS)
    review = sum(1 for t in all_tickets if t.status == TicketStatus.REVIEW)
    todo = sum(1 for t in all_tickets if t.status == TicketStatus.TODO)
    backlog = sum(1 for t in all_tickets if t.status == TicketStatus.BACKLOG)
    return {
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "review": review,
        "todo": todo,
        "backlog": backlog,
        "completion_percent": round(done / total * 100, 1) if total > 0 else 0,
    }


def serialize(obj):
    if isinstance(obj, Enum):
        return obj.value
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            if isinstance(value, list):
                result[field_name] = [serialize(v) for v in value]
            elif isinstance(value, Enum):
                result[field_name] = value.value
            else:
                result[field_name] = value
        return result
    raise TypeError(f"Object of type {type(obj)} is not serializable")


def output_json(data):
    print(json.dumps(data, default=serialize, indent=2))


def cmd_teams(args):
    teams = list_teams()
    output_json([serialize(t) for t in teams])


def cmd_tickets(args):
    status = TicketStatus(args.status) if args.status else None
    tickets = list_tickets(status)
    output_json([serialize(t) for t in tickets])


def cmd_create_ticket(args):
    ticket = create_ticket(args.ticket_id, TicketPriority(args.priority))
    output_json(serialize(ticket))


def cmd_assign_task(args):
    ticket = assign_ticket(args.ticket_id, args.agent_id)
    output_json(serialize(ticket))


def cmd_meetings(args):
    meetings = list_meetings()
    output_json([serialize(m) for m in meetings])


def cmd_attend_meeting(args):
    meeting = attend_meeting(args.meeting_id, args.agent_id)
    output_json(serialize(meeting))


def cmd_progress(args):
    progress = get_progress()
    output_json(progress)


def main():
    parser = argparse.ArgumentParser(prog="company")
    subparsers = parser.add_subparsers(dest="command", required=True)

    teams_parser = subparsers.add_parser("teams", help="List all teams")
    teams_parser.set_defaults(func=cmd_teams)

    tickets_parser = subparsers.add_parser("tickets", help="List tickets")
    tickets_parser.add_argument("--status", help="Filter by status")
    tickets_parser.set_defaults(func=cmd_tickets)

    create_ticket_parser = subparsers.add_parser("create-ticket", help="Create a ticket")
    create_ticket_parser.add_argument("ticket_id")
    create_ticket_parser.add_argument("--priority", default="medium")
    create_ticket_parser.set_defaults(func=cmd_create_ticket)

    assign_parser = subparsers.add_parser("assign-task", help="Assign a task to an agent")
    assign_parser.add_argument("ticket_id")
    assign_parser.add_argument("agent_id")
    assign_parser.set_defaults(func=cmd_assign_task)

    meetings_parser = subparsers.add_parser("meetings", help="List meetings")
    meetings_parser.set_defaults(func=cmd_meetings)

    attend_parser = subparsers.add_parser("attend-meeting", help="Attend a meeting")
    attend_parser.add_argument("meeting_id")
    attend_parser.add_argument("agent_id")
    attend_parser.set_defaults(func=cmd_attend_meeting)

    progress_parser = subparsers.add_parser("progress", help="Check progress")
    progress_parser.set_defaults(func=cmd_progress)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()