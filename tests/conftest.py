import pytest
from src.models.agent import Agent
from src.models.team import Team
from src.models.ticket import Ticket, Subtask
from src.models.meeting import Meeting, MeetingType
from src.models.board import TicketBoard
from src.models.enums import AgentRole, AgentLevel, TicketStatus, TicketPriority, TeamType
from company.github_integration import GitHubIntegration


@pytest.fixture
def agent_role():
    return AgentRole


@pytest.fixture
def agent_level():
    return AgentLevel


@pytest.fixture
def ticket_status():
    return TicketStatus


@pytest.fixture
def ticket_priority():
    return TicketPriority


@pytest.fixture
def team_type():
    return TeamType


@pytest.fixture
def meeting_type():
    return MeetingType


@pytest.fixture
def agent_junior():
    return Agent(
        id="agent-1",
        name="Junior Dev",
        role=AgentRole.DEVELOPER,
        level=AgentLevel.JUNIOR,
        team_id="team-1",
        boss_id="agent-2"
    )


@pytest.fixture
def agent_mid():
    return Agent(
        id="agent-2",
        name="Mid Dev",
        role=AgentRole.DEVELOPER,
        level=AgentLevel.MID,
        team_id="team-1",
        boss_id="agent-3"
    )


@pytest.fixture
def agent_senior():
    return Agent(
        id="agent-3",
        name="Senior Dev",
        role=AgentRole.DEVELOPER,
        level=AgentLevel.SENIOR,
        team_id="team-1",
        boss_id="agent-4"
    )


@pytest.fixture
def agent_lead():
    return Agent(
        id="agent-4",
        name="Team Lead",
        role=AgentRole.DEVELOPER,
        level=AgentLevel.LEAD,
        team_id="team-1"
    )


@pytest.fixture
def agent_po():
    return Agent(
        id="agent-po",
        name="Product Owner",
        role=AgentRole.PO,
        level=AgentLevel.MANAGER,
        team_id="team-1"
    )


@pytest.fixture
def team_engineering():
    return Team(
        id="team-1",
        name="Engineering Team",
        type=TeamType.ENGINEERING,
        leader_id="agent-4",
        member_ids=["agent-1", "agent-2", "agent-3"]
    )


@pytest.fixture
def team_design():
    return Team(
        id="team-2",
        name="Design Team",
        type=TeamType.DESIGN,
        leader_id="agent-designer-lead"
    )


@pytest.fixture
def ticket_backlog():
    return Ticket(
        id="ticket-1",
        title="Test Ticket",
        description="A test ticket",
        status=TicketStatus.BACKLOG,
        priority=TicketPriority.MEDIUM,
        assignee_id="agent-1",
        team_id="team-1",
        reporter_id="agent-po"
    )


@pytest.fixture
def ticket_in_progress():
    return Ticket(
        id="ticket-2",
        title="In Progress Ticket",
        status=TicketStatus.IN_PROGRESS,
        priority=TicketPriority.HIGH,
        assignee_id="agent-2",
        team_id="team-1"
    )


@pytest.fixture
def ticket_done():
    return Ticket(
        id="ticket-3",
        title="Done Ticket",
        status=TicketStatus.DONE,
        priority=TicketPriority.LOW,
        assignee_id="agent-1"
    )


@pytest.fixture
def meeting_standup():
    return Meeting(
        id="meeting-1",
        type=MeetingType.STANDUP,
        team_id="team-1",
        host_id="agent-4",
        participant_ids=["agent-1", "agent-2", "agent-3"]
    )


@pytest.fixture
def meeting_planning():
    return Meeting(
        id="meeting-2",
        type=MeetingType.PLANNING,
        team_id="team-1",
        host_id="agent-po"
    )


@pytest.fixture
def ticket_board():
    return TicketBoard(
        id="board-1",
        name="Main Board",
        team_id="team-1"
    )


@pytest.fixture
def github_integration():
    return GitHubIntegration(repo="owner/repo", token="test-token")