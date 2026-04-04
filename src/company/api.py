from flask import Flask, jsonify, request
from typing import Optional
import uuid
from datetime import datetime

from company import (
    Role, Level, TicketStatus, TicketPriority, TeamType,
    MeetingType, MeetingStatus, Agent, Team, Ticket, Meeting
)
from company.store import get_store


def create_app():
    app = Flask(__name__)
    store = get_store()

    @app.route('/api/health')
    def health():
        return jsonify({"status": "ok"})

    @app.route('/api/agents', methods=['GET'])
    def list_agents():
        team_id = request.args.get('team_id')
        if team_id:
            agents = store.list_agents_by_team(team_id)
        else:
            agents = store.list_agents()
        return jsonify({
            "agents": [a.to_dict() for a in agents]
        })

    @app.route('/api/agents/<agent_id>', methods=['GET'])
    def get_agent(agent_id):
        agent = store.get_agent(agent_id)
        if not agent:
            return jsonify({"error": "Agent not found"}), 404
        return jsonify(agent.to_dict())

    @app.route('/api/agents', methods=['POST'])
    def create_agent():
        data = request.json
        agent = Agent(
            name=data.get('name', ''),
            role=Role(data.get('role', 'developer')),
            level=Level(data.get('level', 1)),
            team_id=data.get('team_id')
        )
        store.add_agent(agent)
        return jsonify(agent.to_dict()), 201

    @app.route('/api/teams', methods=['GET'])
    def list_teams():
        teams = store.list_teams()
        return jsonify({
            "teams": [t.to_dict() for t in teams]
        })

    @app.route('/api/teams/<team_id>', methods=['GET'])
    def get_team(team_id):
        team = store.get_team(team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404
        return jsonify(team.to_dict())

    @app.route('/api/teams', methods=['POST'])
    def create_team():
        data = request.json
        team = Team(
            name=data.get('name', ''),
            type=TeamType(data.get('type', 'engineering')),
            leader_id=data.get('leader_id', '')
        )
        store.add_team(team)
        return jsonify(team.to_dict()), 201

    @app.route('/api/teams/<team_id>/members', methods=['POST'])
    def add_team_member(team_id):
        team = store.get_team(team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404
        data = request.json
        agent_id = data.get('agent_id')
        if not agent_id:
            return jsonify({"error": "agent_id required"}), 400
        team.add_member(agent_id)
        return jsonify(team.to_dict())

    @app.route('/api/tickets', methods=['GET'])
    def list_tickets():
        assignee_id = request.args.get('assignee_id')
        status = request.args.get('status')
        
        tickets = store.list_tickets()
        if assignee_id:
            tickets = [t for t in tickets if t.assignee_id == assignee_id]
        if status:
            tickets = [t for t in tickets if t.status.value == status]
        
        return jsonify({
            "tickets": [t.to_dict() for t in tickets]
        })

    @app.route('/api/tickets/<ticket_id>', methods=['GET'])
    def get_ticket(ticket_id):
        ticket = store.get_ticket(ticket_id)
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        return jsonify(ticket.to_dict())

    @app.route('/api/tickets', methods=['POST'])
    def create_ticket():
        data = request.json
        ticket = Ticket(
            title=data.get('title', ''),
            description=data.get('description', ''),
            priority=TicketPriority(data.get('priority', 'medium')),
            assignee_id=data.get('assignee_id')
        )
        store.add_ticket(ticket)
        return jsonify(ticket.to_dict()), 201

    @app.route('/api/tickets/<ticket_id>', methods=['PATCH'])
    def update_ticket(ticket_id):
        ticket = store.get_ticket(ticket_id)
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        
        data = request.json
        if 'status' in data:
            ticket.status = TicketStatus(data['status'])
        if 'priority' in data:
            ticket.priority = TicketPriority(data['priority'])
        if 'assignee_id' in data:
            ticket.assignee_id = data['assignee_id']
        if 'title' in data:
            ticket.title = data['title']
        if 'description' in data:
            ticket.description = data['description']
        
        ticket.updated_at = datetime.utcnow()
        return jsonify(ticket.to_dict())

    @app.route('/api/tickets/<ticket_id>/assign', methods=['POST'])
    def assign_ticket(ticket_id):
        ticket = store.get_ticket(ticket_id)
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        data = request.json
        agent_id = data.get('agent_id')
        if not agent_id:
            return jsonify({"error": "agent_id required"}), 400
        ticket.assignee_id = agent_id
        ticket.updated_at = datetime.utcnow()
        return jsonify(ticket.to_dict())

    @app.route('/api/meetings', methods=['GET'])
    def list_meetings():
        team_id = request.args.get('team_id')
        if team_id:
            meetings = store.list_meetings_by_team(team_id)
        else:
            meetings = store.list_meetings()
        return jsonify({
            "meetings": [m.to_dict() for m in meetings]
        })

    @app.route('/api/meetings/<meeting_id>', methods=['GET'])
    def get_meeting(meeting_id):
        meeting = store.get_meeting(meeting_id)
        if not meeting:
            return jsonify({"error": "Meeting not found"}), 404
        return jsonify(meeting.to_dict())

    @app.route('/api/meetings', methods=['POST'])
    def create_meeting():
        data = request.json
        meeting = Meeting(
            type=MeetingType(data.get('type', 'daily_standup')),
            title=data.get('title', ''),
            team_id=data.get('team_id', ''),
            sprint_id=data.get('sprint_id'),
            created_by=data.get('created_by', '')
        )
        store.add_meeting(meeting)
        return jsonify(meeting.to_dict()), 201

    @app.route('/api/meetings/<meeting_id>/attend', methods=['POST'])
    def attend_meeting(meeting_id):
        meeting = store.get_meeting(meeting_id)
        if not meeting:
            return jsonify({"error": "Meeting not found"}), 404
        data = request.json
        agent_id = data.get('agent_id')
        if not agent_id:
            return jsonify({"error": "agent_id required"}), 400
        meeting.add_participant(agent_id)
        return jsonify(meeting.to_dict())

    @app.route('/api/meetings/<meeting_id>/start', methods=['POST'])
    def start_meeting(meeting_id):
        meeting = store.get_meeting(meeting_id)
        if not meeting:
            return jsonify({"error": "Meeting not found"}), 404
        data = request.json
        agent_id = data.get('agent_id', '')
        if not meeting.start_meeting(agent_id):
            return jsonify({"error": "Cannot start meeting"}), 400
        return jsonify(meeting.to_dict())

    @app.route('/api/meetings/<meeting_id>/end', methods=['POST'])
    def end_meeting(meeting_id):
        meeting = store.get_meeting(meeting_id)
        if not meeting:
            return jsonify({"error": "Meeting not found"}), 404
        meeting.end_meeting()
        return jsonify(meeting.to_dict())

    @app.route('/api/progress/team/<team_id>', methods=['GET'])
    def team_progress(team_id):
        team = store.get_team(team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404
        
        tickets = store.list_tickets()
        status_counts = {}
        for status in TicketStatus:
            status_counts[status.value] = 0
        for ticket in tickets:
            status_counts[ticket.status.value] += 1
        
        return jsonify({
            "team_id": team_id,
            "team_name": team.name,
            "ticket_counts": status_counts,
            "total_tickets": len(tickets)
        })

    @app.route('/api/progress/agent/<agent_id>', methods=['GET'])
    def agent_progress(agent_id):
        agent = store.get_agent(agent_id)
        if not agent:
            return jsonify({"error": "Agent not found"}), 404
        
        tickets = store.list_tickets_by_assignee(agent_id)
        status_counts = {}
        for status in TicketStatus:
            status_counts[status.value] = 0
        for ticket in tickets:
            status_counts[ticket.status.value] += 1
        
        return jsonify({
            "agent_id": agent_id,
            "agent_name": agent.name,
            "ticket_counts": status_counts,
            "total_tickets": len(tickets)
        })

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)