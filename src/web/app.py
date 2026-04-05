from flask import render_template, jsonify, request
from . import app
from ..models.company import Company
from ..models.enums import AgentRole, AgentLevel, TeamType, TicketStatus, TicketPriority
from ..models.meeting import MeetingType
import uuid


company = Company()
_sample_data_initialized = False


def _init_sample_data():
    global _sample_data_initialized
    if _sample_data_initialized:
        return
    
    ceo = company.create_agent("CEO Agent", AgentRole.PO, AgentLevel.DIRECTOR)
    
    cto = company.create_agent("CTO", AgentRole.DEVELOPER, AgentLevel.DIRECTOR, boss_id=ceo.id)
    cpo = company.create_agent("CPO", AgentRole.PO, AgentLevel.DIRECTOR, boss_id=ceo.id)
    
    eng_lead = company.create_agent("Engineering Lead", AgentRole.DEVELOPER, AgentLevel.MANAGER, boss_id=cto.id)
    design_lead = company.create_agent("Design Lead", AgentRole.DESIGNER, AgentLevel.MANAGER, boss_id=cpo.id)
    
    eng_team = company.create_team("Engineering Team", TeamType.ENGINEERING, leader_id=eng_lead.id)
    product_team = company.create_team("Product Team", TeamType.PRODUCT, leader_id=cpo.id)
    design_team = company.create_team("Design Team", TeamType.DESIGN, leader_id=design_lead.id)
    
    dev1 = company.create_agent("Senior Developer", AgentRole.DEVELOPER, AgentLevel.SENIOR, team_id=eng_team.id, boss_id=eng_lead.id)
    dev2 = company.create_agent("Developer", AgentRole.DEVELOPER, AgentLevel.MID, team_id=eng_team.id, boss_id=eng_lead.id)
    dev3 = company.create_agent("Junior Developer", AgentRole.DEVELOPER, AgentLevel.JUNIOR, team_id=eng_team.id, boss_id=dev1.id)
    
    des1 = company.create_agent("Senior Designer", AgentRole.DESIGNER, AgentLevel.SENIOR, team_id=design_team.id, boss_id=design_lead.id)
    des2 = company.create_agent("Designer", AgentRole.DESIGNER, AgentLevel.MID, team_id=design_team.id, boss_id=des1.id)
    
    board = company.create_board("Main Board", team_id=eng_team.id)
    
    t1 = company.create_ticket("Implement user authentication", "Add OAuth and JWT auth", team_id=eng_team.id, priority=TicketPriority.HIGH)
    company.assign_ticket(t1.id, dev1.id)
    t1.set_status(TicketStatus.IN_PROGRESS)
    
    t2 = company.create_ticket("Design landing page", "Create wireframes and mockups", team_id=design_team.id, priority=TicketPriority.MEDIUM)
    company.assign_ticket(t2.id, des1.id)
    t2.set_status(TicketStatus.TODO)
    
    t3 = company.create_ticket("API documentation", "Document all REST endpoints", team_id=eng_team.id, priority=TicketPriority.LOW)
    t3.set_status(TicketStatus.BACKLOG)
    
    t4 = company.create_ticket("Fix login bug", "Users cannot reset password", team_id=eng_team.id, priority=TicketPriority.CRITICAL)
    company.assign_ticket(t4.id, dev2.id)
    t4.set_status(TicketStatus.REVIEW)
    
    t5 = company.create_ticket("Update dependencies", "Upgrade all npm packages", team_id=eng_team.id, priority=TicketPriority.LOW)
    company.assign_ticket(t5.id, dev3.id)
    t5.set_status(TicketStatus.DONE)
    
    standup = company.create_meeting(MeetingType.STANDUP, eng_team.id, eng_lead.id)
    
    _sample_data_initialized = True


@app.route('/')
def index():
    _init_sample_data()
    return render_template('index.html')


@app.route('/hierarchy')
def hierarchy_page():
    _init_sample_data()
    return render_template('hierarchy.html')


@app.route('/tickets')
def tickets_page():
    _init_sample_data()
    return render_template('tickets.html')


@app.route('/teams')
def teams_page():
    _init_sample_data()
    return render_template('teams.html')


@app.route('/chat')
def chat_page():
    _init_sample_data()
    return render_template('chat.html')


@app.route('/api/agents')
def get_agents():
    _init_sample_data()
    agents = []
    for agent in company.agents.values():
        boss = company.agents.get(agent.boss_id) if agent.boss_id else None
        team = company.teams.get(agent.team_id) if agent.team_id else None
        agents.append({
            'id': agent.id,
            'name': agent.name,
            'role': agent.role.value,
            'level': agent.level.name,
            'boss_id': agent.boss_id,
            'boss_name': boss.name if boss else None,
            'team_id': agent.team_id,
            'team_name': team.name if team else None
        })
    return jsonify(agents)


@app.route('/api/teams')
def get_teams():
    _init_sample_data()
    teams = []
    for team in company.teams.values():
        leader = company.agents.get(team.leader_id)
        members = [company.agents.get(mid) for mid in team.member_ids if mid in company.agents]
        teams.append({
            'id': team.id,
            'name': team.name,
            'type': team.type.value,
            'leader_id': team.leader_id,
            'leader_name': leader.name if leader else None,
            'member_ids': team.member_ids,
            'members': [{'id': m.id, 'name': m.name} for m in members if m],
            'member_count': len(members)
        })
    return jsonify(teams)


@app.route('/api/tickets')
def get_tickets():
    _init_sample_data()
    tickets = []
    for ticket in company.tickets.values():
        assignee = company.agents.get(ticket.assignee_id) if ticket.assignee_id else None
        team = company.teams.get(ticket.team_id) if ticket.team_id else None
        tickets.append({
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'status': ticket.status.value,
            'priority': ticket.priority.value,
            'assignee_id': ticket.assignee_id,
            'assignee_name': assignee.name if assignee else None,
            'team_id': ticket.team_id,
            'team_name': team.name if team else None,
            'created_at': ticket.created_at.isoformat() if ticket.created_at else None
        })
    return jsonify(tickets)


@app.route('/api/hierarchy')
def get_hierarchy():
    _init_sample_data()
    
    def build_tree(agent_id):
        agent = company.agents.get(agent_id)
        if not agent:
            return None
        
        children = []
        for a in company.agents.values():
            if a.boss_id == agent_id:
                child = build_tree(a.id)
                if child:
                    children.append(child)
        
        team = company.teams.get(agent.team_id) if agent.team_id else None
        
        return {
            'id': agent.id,
            'name': agent.name,
            'role': agent.role.value,
            'level': agent.level.name,
            'team': team.name if team else None,
            'children': children
        }
    
    root_agents = [a for a in company.agents.values() if a.boss_id is None]
    hierarchy = [build_tree(a.id) for a in root_agents if build_tree(a.id)]
    
    return jsonify(hierarchy)


@app.route('/api/chat', methods=['POST'])
def chat():
    _init_sample_data()
    data = request.json
    
    agent_id = data.get('agent_id')
    message = data.get('message', '')
    
    if not agent_id or agent_id not in company.agents:
        return jsonify({'error': 'Invalid agent ID'}), 400
    
    agent = company.agents[agent_id]
    
    responses = [
        f"I'm {agent.name}, working as {agent.role.value}. How can I help you?",
        f"Sure, I can help with that. I'm currently on the {agent.name} team.",
        f"Let me check my tasks and get back to you.",
        f"I understand. What would you like to discuss?",
    ]
    
    import random
    response = random.choice(responses)
    
    return jsonify({
        'agent_id': agent_id,
        'agent_name': agent.name,
        'response': response
    })


@app.route('/api/meeting/<meeting_id>/join', methods=['POST'])
def join_meeting(meeting_id):
    _init_sample_data()
    data = request.json
    
    meeting = company.meetings.get(meeting_id)
    if not meeting:
        return jsonify({'error': 'Meeting not found'}), 404
    
    user_type = data.get('user_type', 'human')
    user_id = data.get('user_id', f"user-{uuid.uuid4().hex[:8]}")
    
    if user_type == 'human':
        meeting.add_participant(user_id)
        
        if 'client-ai' not in meeting.participant_ids:
            meeting.add_participant('client-ai')
            client_role = "AI Client"
        else:
            client_role = None
        
        return jsonify({
            'meeting_id': meeting_id,
            'user_id': user_id,
            'user_type': 'human',
            'message': 'Joined meeting as human participant',
            'client_role': client_role
        })
    else:
        return jsonify({'error': 'Invalid user type'}), 400


@app.route('/api/meetings')
def get_meetings():
    _init_sample_data()
    meetings = []
    for meeting in company.meetings.values():
        host = company.agents.get(meeting.host_id)
        team = company.teams.get(meeting.team_id) if meeting.team_id else None
        meetings.append({
            'id': meeting.id,
            'type': meeting.type.value,
            'host_id': meeting.host_id,
            'host_name': host.name if host else None,
            'team_id': meeting.team_id,
            'team_name': team.name if team else None,
            'participant_ids': meeting.participant_ids,
            'participant_count': len(meeting.participant_ids)
        })
    return jsonify(meetings)