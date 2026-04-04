import click
import json
import uuid
from datetime import datetime
from typing import Optional

from company import (
    Role, Level, TicketStatus, TicketPriority, TeamType,
    MeetingType, MeetingStatus, Agent, Team, Ticket, Meeting
)
from company.store import get_store


def output_json(data: dict, pretty: bool = False) -> None:
    if pretty:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        click.echo(json.dumps(data, default=str))


@click.group()
@click.option('--pretty', is_flag=True, help='Pretty print JSON output')
@click.pass_context
def cli(ctx, pretty):
    ctx.ensure_object(dict)
    ctx.obj['pretty'] = pretty


@cli.group()
def teams():
    pass


@teams.command('list')
@click.pass_context
def teams_list(ctx):
    store = get_store()
    teams = store.list_teams()
    output_json({
        "teams": [t.to_dict() for t in teams]
    }, ctx.obj['pretty'])


@teams.command('view')
@click.argument('team_id')
@click.pass_context
def teams_view(ctx, team_id):
    store = get_store()
    team = store.get_team(team_id)
    if not team:
        raise click.ClickException(f"Team not found: {team_id}")
    output_json(team.to_dict(), ctx.obj['pretty'])


@teams.command('create')
@click.option('--name', required=True, help='Team name')
@click.option('--type', 'team_type', type=click.Choice(['product', 'engineering', 'design', 'operations', 'executive']), default='engineering')
@click.option('--leader-id', help='Leader agent ID')
@click.pass_context
def teams_create(ctx, name, team_type, leader_id):
    store = get_store()
    team = Team(
        name=name,
        type=TeamType(team_type),
        leader_id=leader_id or ""
    )
    store.add_team(team)
    output_json(team.to_dict(), ctx.obj['pretty'])


@teams.command('add-member')
@click.argument('team_id')
@click.argument('agent_id')
@click.pass_context
def teams_add_member(ctx, team_id, agent_id):
    store = get_store()
    team = store.get_team(team_id)
    if not team:
        raise click.ClickException(f"Team not found: {team_id}")
    team.add_member(agent_id)
    output_json(team.to_dict(), ctx.obj['pretty'])


@cli.group()
def tickets():
    pass


@tickets.command('list')
@click.option('--team-id', help='Filter by team')
@click.option('--assignee-id', help='Filter by assignee')
@click.option('--status', help='Filter by status')
@click.pass_context
def tickets_list(ctx, team_id, assignee_id, status):
    store = get_store()
    all_tickets = store.list_tickets()
    
    filtered = all_tickets
    if assignee_id:
        filtered = [t for t in filtered if t.assignee_id == assignee_id]
    if status:
        filtered = [t for t in filtered if t.status.value == status]
    
    output_json({
        "tickets": [t.to_dict() for t in filtered]
    }, ctx.obj['pretty'])


@tickets.command('view')
@click.argument('ticket_id')
@click.pass_context
def tickets_view(ctx, ticket_id):
    store = get_store()
    ticket = store.get_ticket(ticket_id)
    if not ticket:
        raise click.ClickException(f"Ticket not found: {ticket_id}")
    output_json(ticket.to_dict(), ctx.obj['pretty'])


@tickets.command('create')
@click.option('--title', required=True, help='Ticket title')
@click.option('--description', help='Ticket description')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high', 'critical']), default='medium')
@click.option('--assignee-id', help='Assignee agent ID')
@click.option('--team-id', help='Team ID for the ticket')
@click.pass_context
def tickets_create(ctx, title, description, priority, assignee_id, team_id):
    store = get_store()
    ticket = Ticket(
        title=title,
        description=description or "",
        priority=TicketPriority(priority),
        assignee_id=assignee_id
    )
    store.add_ticket(ticket)
    output_json(ticket.to_dict(), ctx.obj['pretty'])


@tickets.command('assign')
@click.argument('ticket_id')
@click.argument('agent_id')
@click.pass_context
def tickets_assign(ctx, ticket_id, agent_id):
    store = get_store()
    ticket = store.get_ticket(ticket_id)
    if not ticket:
        raise click.ClickException(f"Ticket not found: {ticket_id}")
    ticket.assignee_id = agent_id
    ticket.updated_at = datetime.utcnow()
    output_json(ticket.to_dict(), ctx.obj['pretty'])


@tickets.command('update-status')
@click.argument('ticket_id')
@click.argument('status')
@click.pass_context
def tickets_update_status(ctx, ticket_id, status):
    store = get_store()
    ticket = store.get_ticket(ticket_id)
    if not ticket:
        raise click.ClickException(f"Ticket not found: {ticket_id}")
    try:
        ticket.status = TicketStatus(status)
    except ValueError:
        raise click.ClickException(f"Invalid status: {status}")
    ticket.updated_at = datetime.utcnow()
    output_json(ticket.to_dict(), ctx.obj['pretty'])


@cli.group()
def meetings():
    pass


@meetings.command('list')
@click.option('--team-id', help='Filter by team')
@click.pass_context
def meetings_list(ctx, team_id):
    store = get_store()
    if team_id:
        meetings = store.list_meetings_by_team(team_id)
    else:
        meetings = store.list_meetings()
    output_json({
        "meetings": [m.to_dict() for m in meetings]
    }, ctx.obj['pretty'])


@meetings.command('view')
@click.argument('meeting_id')
@click.pass_context
def meetings_view(ctx, meeting_id):
    store = get_store()
    meeting = store.get_meeting(meeting_id)
    if not meeting:
        raise click.ClickException(f"Meeting not found: {meeting_id}")
    output_json(meeting.to_dict(), ctx.obj['pretty'])


@meetings.command('create')
@click.option('--type', 'meeting_type', type=click.Choice(['daily_standup', 'sprint_planning', 'retrospective']), default='daily_standup')
@click.option('--title', help='Meeting title')
@click.option('--team-id', required=True, help='Team ID')
@click.option('--sprint-id', help='Sprint ID')
@click.pass_context
def meetings_create(ctx, meeting_type, title, team_id, sprint_id):
    store = get_store()
    meeting = Meeting(
        type=MeetingType(meeting_type),
        title=title or f"{meeting_type.replace('_', ' ').title()} - {datetime.utcnow().isoformat()}",
        team_id=team_id,
        sprint_id=sprint_id,
        created_by=""
    )
    store.add_meeting(meeting)
    output_json(meeting.to_dict(), ctx.obj['pretty'])


@meetings.command('attend')
@click.argument('meeting_id')
@click.argument('agent_id')
@click.pass_context
def meetings_attend(ctx, meeting_id, agent_id):
    store = get_store()
    meeting = store.get_meeting(meeting_id)
    if not meeting:
        raise click.ClickException(f"Meeting not found: {meeting_id}")
    meeting.add_participant(agent_id)
    output_json(meeting.to_dict(), ctx.obj['pretty'])


@meetings.command('start')
@click.argument('meeting_id')
@click.argument('agent_id')
@click.pass_context
def meetings_start(ctx, meeting_id, agent_id):
    store = get_store()
    meeting = store.get_meeting(meeting_id)
    if not meeting:
        raise click.ClickException(f"Meeting not found: {meeting_id}")
    if not meeting.start_meeting(agent_id):
        raise click.ClickException("Cannot start meeting")
    output_json(meeting.to_dict(), ctx.obj['pretty'])


@meetings.command('end')
@click.argument('meeting_id')
@click.pass_context
def meetings_end(ctx, meeting_id):
    store = get_store()
    meeting = store.get_meeting(meeting_id)
    if not meeting:
        raise click.ClickException(f"Meeting not found: {meeting_id}")
    meeting.end_meeting()
    output_json(meeting.to_dict(), ctx.obj['pretty'])


@cli.group()
def agents():
    pass


@agents.command('list')
@click.option('--team-id', help='Filter by team')
@click.pass_context
def agents_list(ctx, team_id):
    store = get_store()
    if team_id:
        agents = store.list_agents_by_team(team_id)
    else:
        agents = store.list_agents()
    output_json({
        "agents": [a.to_dict() for a in agents]
    }, ctx.obj['pretty'])


@agents.command('view')
@click.argument('agent_id')
@click.pass_context
def agents_view(ctx, agent_id):
    store = get_store()
    agent = store.get_agent(agent_id)
    if not agent:
        raise click.ClickException(f"Agent not found: {agent_id}")
    output_json(agent.to_dict(), ctx.obj['pretty'])


@agents.command('create')
@click.option('--name', required=True, help='Agent name')
@click.option('--role', type=click.Choice(['product_owner', 'developer', 'designer', 'reviewer', 'hr', 'client']), default='developer')
@click.option('--level', type=click.IntRange(1, 10), default=1)
@click.option('--team-id', help='Team ID')
@click.pass_context
def agents_create(ctx, name, role, level, team_id):
    store = get_store()
    agent = Agent(
        name=name,
        role=Role(role),
        level=Level[f"L{level}"],
        team_id=team_id
    )
    store.add_agent(agent)
    output_json(agent.to_dict(), ctx.obj['pretty'])


@cli.group()
def progress():
    pass


@progress.command('team')
@click.argument('team_id')
@click.pass_context
def progress_team(ctx, team_id):
    store = get_store()
    team = store.get_team(team_id)
    if not team:
        raise click.ClickException(f"Team not found: {team_id}")
    
    tickets = [t for t in store.list_tickets()]
    status_counts = {}
    for status in TicketStatus:
        status_counts[status.value] = 0
    for ticket in tickets:
        status_counts[ticket.status.value] += 1
    
    output_json({
        "team_id": team_id,
        "team_name": team.name,
        "ticket_counts": status_counts,
        "total_tickets": len(tickets)
    }, ctx.obj['pretty'])


@progress.command('agent')
@click.argument('agent_id')
@click.pass_context
def progress_agent(ctx, agent_id):
    store = get_store()
    agent = store.get_agent(agent_id)
    if not agent:
        raise click.ClickException(f"Agent not found: {agent_id}")
    
    tickets = store.list_tickets_by_assignee(agent_id)
    status_counts = {}
    for status in TicketStatus:
        status_counts[status.value] = 0
    for ticket in tickets:
        status_counts[ticket.status.value] += 1
    
    output_json({
        "agent_id": agent_id,
        "agent_name": agent.name,
        "ticket_counts": status_counts,
        "total_tickets": len(tickets)
    }, ctx.obj['pretty'])


if __name__ == '__main__':
    cli()