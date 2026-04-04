from typing import Optional, Dict, List, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field

from ..ceo import CEOAgent
from .agent import Agent
from .team import Team
from .ticket import Ticket
from .board import TicketBoard
from .meeting import Meeting, MeetingType
from .enums import AgentRole, AgentLevel, TeamType, TicketStatus, TicketPriority

if TYPE_CHECKING:
    from ..workflow import WorkflowEngine, WorkflowEvent
else:
    WorkflowEngine = None
    WorkflowEvent = None


@dataclass
class Company:
    agents: Dict[str, Agent] = field(default_factory=dict)
    teams: Dict[str, Team] = field(default_factory=dict)
    tickets: Dict[str, Ticket] = field(default_factory=dict)
    boards: Dict[str, TicketBoard] = field(default_factory=dict)
    meetings: Dict[str, Meeting] = field(default_factory=dict)
    workflow_engine: Optional[WorkflowEngine] = None
    next_agent_id: int = 1
    next_team_id: int = 1
    next_ticket_id: int = 1
    next_meeting_id: int = 1

    @classmethod
    def bootstrap(cls, task_description: str) -> "Company":
        company = cls()
        ceo = CEOAgent(company)
        return ceo.bootstrap(task_description)

    def create_agent(self, name: str, role: AgentRole, level: AgentLevel, 
                     team_id: Optional[str] = None, boss_id: Optional[str] = None) -> Agent:
        agent_id = f"agent-{self.next_agent_id}"
        self.next_agent_id += 1
        agent = Agent(
            id=agent_id,
            name=name,
            role=role,
            level=level,
            team_id=team_id,
            boss_id=boss_id
        )
        self.agents[agent_id] = agent
        
        if team_id and team_id in self.teams:
            self.teams[team_id].add_member(agent_id)
        
        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def create_team(self, name: str, team_type: TeamType, leader_id: str,
                    parent_team_id: Optional[str] = None) -> Team:
        team_id = f"team-{self.next_team_id}"
        self.next_team_id += 1
        team = Team(
            id=team_id,
            name=name,
            type=team_type,
            leader_id=leader_id,
            parent_team_id=parent_team_id
        )
        self.teams[team_id] = team
        
        if parent_team_id and parent_team_id in self.teams:
            self.teams[parent_team_id].add_subteam(team_id)
        
        leader = self.agents.get(leader_id)
        if leader:
            leader.team_id = team_id
        
        return team

    def get_team(self, team_id: str) -> Optional[Team]:
        return self.teams.get(team_id)

    def recruit_to_team(self, leader_id: str, new_agent_name: str, 
                        role: AgentRole, level: AgentLevel) -> Optional[Agent]:
        leader = self.agents.get(leader_id)
        if not leader or not leader.team_id:
            return None
        
        team = self.teams.get(leader.team_id)
        if not team or not team.is_leader(leader_id):
            return None
        
        new_agent = self.create_agent(
            name=new_agent_name,
            role=role,
            level=level,
            team_id=leader.team_id,
            boss_id=leader_id
        )
        
        return new_agent

    def form_subteam(self, leader_id: str, subteam_name: str, 
                     subteam_type: TeamType) -> Optional[Team]:
        leader = self.agents.get(leader_id)
        if not leader or not leader.team_id:
            return None
        
        team = self.teams.get(leader.team_id)
        if not team or not team.is_leader(leader_id):
            return None
        
        subteam = self.create_team(
            name=subteam_name,
            team_type=TeamType.SUBTEAM,
            leader_id=leader_id,
            parent_team_id=leader.team_id
        )
        
        return subteam

    def create_ticket(self, title: str, description: str = "",
                      team_id: Optional[str] = None,
                      reporter_id: Optional[str] = None,
                      priority: TicketPriority = TicketPriority.MEDIUM,
                      complexity_estimate: Optional[int] = None) -> Ticket:
        ticket_id = f"ticket-{self.next_ticket_id}"
        self.next_ticket_id += 1
        ticket = Ticket(
            id=ticket_id,
            title=title,
            description=description,
            team_id=team_id,
            reporter_id=reporter_id,
            priority=priority,
            complexity_estimate=complexity_estimate,
            status=TicketStatus.BACKLOG
        )
        self.tickets[ticket_id] = ticket
        return ticket

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return self.tickets.get(ticket_id)

    def assign_ticket(self, ticket_id: str, agent_id: str) -> bool:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        if agent_id not in self.agents:
            return False
        ticket.assign(agent_id)
        return True

    def lock_ticket(self, ticket_id: str, agent_id: str) -> bool:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        return ticket.lock(agent_id)

    def unlock_ticket(self, ticket_id: str, agent_id: str) -> bool:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        return ticket.unlock(agent_id)

    def create_board(self, name: str, team_id: Optional[str] = None) -> TicketBoard:
        board_id = f"board-{len(self.boards) + 1}"
        board = TicketBoard(id=board_id, name=name, team_id=team_id)
        self.boards[board_id] = board
        return board

    def get_board(self, board_id: str) -> Optional[TicketBoard]:
        return self.boards.get(board_id)

    def add_ticket_to_team_swimlane(self, board_id: str, team_id: str, 
                                     ticket_id: str) -> bool:
        board = self.boards.get(board_id)
        if not board:
            return False
        board.add_ticket_to_swimlane(team_id, ticket_id)
        return True

    def get_team_tickets(self, team_id: str) -> List[Ticket]:
        return [t for t in self.tickets.values() if t.team_id == team_id]

    def get_tickets_by_status(self, status: TicketStatus) -> List[Ticket]:
        return [t for t in self.tickets.values() if t.status == status]

    def get_tickets_by_assignee(self, agent_id: str) -> List[Ticket]:
        return [t for t in self.tickets.values() if t.assignee_id == agent_id]

    def get_locked_tickets(self) -> List[Ticket]:
        return [t for t in self.tickets.values() if t.is_locked()]

    def transfer_ticket(self, ticket_id: str, to_agent_id: str) -> bool:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        if to_agent_id not in self.agents:
            return False
        ticket.assignee_id = to_agent_id
        return True

    def reassign_ticket_to_team(self, ticket_id: str, team_id: str) -> bool:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        if team_id not in self.teams:
            return False
        ticket.team_id = team_id
        return True

    def create_meeting(self, meeting_type: MeetingType, team_id: str, host_id: str) -> Meeting:
        meeting_id = f"meeting-{self.next_meeting_id}"
        self.next_meeting_id += 1
        meeting = Meeting(
            id=meeting_id,
            type=meeting_type,
            team_id=team_id,
            host_id=host_id
        )
        self.meetings[meeting_id] = meeting
        
        team = self.teams.get(team_id)
        if team:
            for member_id in team.member_ids:
                meeting.add_participant(member_id)
        
        return meeting

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        return self.meetings.get(meeting_id)

    def start_workflow_engine(self) -> None:
        if self.workflow_engine is None:
            from ..workflow import WorkflowEngine
            self.workflow_engine = WorkflowEngine()
            self.workflow_engine.initialize(self)
        self.workflow_engine.start()

    def stop_workflow_engine(self) -> None:
        if self.workflow_engine:
            self.workflow_engine.stop()

    def complete_ticket(self, agent_id: str, ticket_id: str) -> Optional[str]:
        ticket = self.tickets.get(ticket_id)
        if not ticket or ticket.assignee_id != agent_id:
            return None
        
        ticket.set_status(TicketStatus.DONE)
        
        if self.workflow_engine and self.workflow_engine.is_running():
            from ..workflow.triggers import WorkflowEvent
            self.workflow_engine.emit_event(
                WorkflowEvent.TICKET_COMPLETED,
                agent_id=agent_id,
                team_id=ticket.team_id,
                ticket_id=ticket_id
            )
        
        return ticket_id

    def pick_next_ticket(self, agent_id: str) -> Optional[Ticket]:
        agent = self.agents.get(agent_id)
        if not agent or not agent.team_id:
            return None
        
        team = self.teams.get(agent.team_id)
        if not team:
            return None
        
        for ticket in self.tickets.values():
            if ticket.team_id == agent.team_id and ticket.status in [
                TicketStatus.BACKLOG,
                TicketStatus.TODO
            ] and not ticket.assignee_id:
                ticket.assign(agent_id)
                ticket.set_status(TicketStatus.IN_PROGRESS)
                return ticket
        
        return None

    def report_blocker(self, agent_id: str, ticket_id: str, reason: str) -> None:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return
        
        if self.workflow_engine and self.workflow_engine.is_running():
            from ..workflow.triggers import WorkflowEvent
            self.workflow_engine.emit_event(
                WorkflowEvent.TICKET_BLOCKED,
                agent_id=agent_id,
                team_id=ticket.team_id,
                ticket_id=ticket_id,
                metadata={"reason": reason}
            )

    def check_team_completion(self, team_id: str) -> bool:
        team = self.teams.get(team_id)
        if not team:
            return False
        return team.check_completion(list(self.tickets.values()))

    def trigger_team_completion(self, team_id: str, sprint_ended: bool = False) -> None:
        if self.workflow_engine and self.workflow_engine.is_running():
            from ..workflow.triggers import WorkflowEvent
            self.workflow_engine.emit_event(
                WorkflowEvent.TEAM_COMPLETED,
                agent_id="",
                team_id=team_id,
                metadata={"sprint_ended": sprint_ended}
            )