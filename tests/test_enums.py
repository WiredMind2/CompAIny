import pytest
from src.models.enums import (
    AgentRole,
    AgentLevel,
    TicketStatus,
    TicketPriority,
    TeamType,
)


class TestAgentRole:
    def test_all_roles_exist(self):
        assert AgentRole.PO.value == "PO"
        assert AgentRole.DEVELOPER.value == "DEVELOPER"
        assert AgentRole.DESIGNER.value == "DESIGNER"
        assert AgentRole.REVIEWER.value == "REVIEWER"
        assert AgentRole.HR.value == "HR"
        assert AgentRole.CLIENT.value == "CLIENT"

    def test_role_count(self):
        roles = list(AgentRole)
        assert len(roles) == 6

    def test_role_is_string(self):
        assert isinstance(AgentRole.PO.value, str)
        assert isinstance(AgentRole.DEVELOPER.value, str)


class TestAgentLevel:
    def test_all_levels_exist(self):
        assert AgentLevel.JUNIOR.value == 1
        assert AgentLevel.MID.value == 2
        assert AgentLevel.SENIOR.value == 3
        assert AgentLevel.LEAD.value == 4
        assert AgentLevel.MANAGER.value == 5
        assert AgentLevel.DIRECTOR.value == 6
        assert AgentLevel.VP.value == 7
        assert AgentLevel.C_LEVEL.value == 8
        assert AgentLevel.FOUNDER.value == 9
        assert AgentLevel.BOARD.value == 10

    def test_level_count(self):
        levels = list(AgentLevel)
        assert len(levels) == 10

    def test_level_is_int(self):
        assert isinstance(AgentLevel.JUNIOR.value, int)
        assert isinstance(AgentLevel.MID.value, int)
        assert isinstance(AgentLevel.SENIOR.value, int)

    def test_level_ordering(self):
        assert AgentLevel.JUNIOR < AgentLevel.MID
        assert AgentLevel.MID < AgentLevel.SENIOR
        assert AgentLevel.SENIOR < AgentLevel.LEAD
        assert AgentLevel.LEAD < AgentLevel.MANAGER


class TestTicketStatus:
    def test_all_statuses_exist(self):
        assert TicketStatus.BACKLOG.value == "backlog"
        assert TicketStatus.TODO.value == "todo"
        assert TicketStatus.IN_PROGRESS.value == "in_progress"
        assert TicketStatus.REVIEW.value == "review"
        assert TicketStatus.DONE.value == "done"

    def test_status_count(self):
        statuses = list(TicketStatus)
        assert len(statuses) == 5

    def test_status_is_string(self):
        assert isinstance(TicketStatus.BACKLOG.value, str)
        assert isinstance(TicketStatus.IN_PROGRESS.value, str)


class TestTicketPriority:
    def test_all_priorities_exist(self):
        assert TicketPriority.LOW.value == "low"
        assert TicketPriority.MEDIUM.value == "medium"
        assert TicketPriority.HIGH.value == "high"
        assert TicketPriority.CRITICAL.value == "critical"

    def test_priority_count(self):
        priorities = list(TicketPriority)
        assert len(priorities) == 4

    def test_priority_is_string(self):
        assert isinstance(TicketPriority.LOW.value, str)
        assert isinstance(TicketPriority.HIGH.value, str)


class TestTeamType:
    def test_all_types_exist(self):
        assert TeamType.ENGINEERING.value == "engineering"
        assert TeamType.DESIGN.value == "design"
        assert TeamType.PRODUCT.value == "product"
        assert TeamType.OPERATIONS.value == "operations"
        assert TeamType.EXECUTIVE.value == "executive"
        assert TeamType.SUBTEAM.value == "subteam"

    def test_type_count(self):
        types = list(TeamType)
        assert len(types) == 6

    def test_type_is_string(self):
        assert isinstance(TeamType.ENGINEERING.value, str)
        assert isinstance(TeamType.DESIGN.value, str)