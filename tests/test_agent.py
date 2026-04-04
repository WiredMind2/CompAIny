import pytest
from src.models.agent import Agent
from src.models.enums import AgentRole, AgentLevel


class TestAgentCreation:
    def test_agent_creation_minimal(self):
        agent = Agent(
            id="agent-1",
            name="Test Agent",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR
        )
        assert agent.id == "agent-1"
        assert agent.name == "Test Agent"
        assert agent.role == AgentRole.DEVELOPER
        assert agent.level == AgentLevel.JUNIOR

    def test_agent_creation_full(self, agent_junior):
        assert agent_junior.id == "agent-1"
        assert agent_junior.name == "Junior Dev"
        assert agent_junior.role == AgentRole.DEVELOPER
        assert agent_junior.level == AgentLevel.JUNIOR
        assert agent_junior.team_id == "team-1"
        assert agent_junior.boss_id == "agent-2"

    def test_agent_creation_with_team(self, agent_mid):
        assert agent_mid.team_id == "team-1"
        assert agent_mid.boss_id == "agent-3"

    def test_agent_creation_no_boss(self, agent_lead):
        assert agent_lead.boss_id is None


class TestCanMessage:
    def test_cannot_message_self(self, agent_junior):
        assert agent_junior.can_message(agent_junior) is False

    def test_can_message_boss(self, agent_junior, agent_mid):
        assert agent_junior.can_message(agent_mid) is True

    def test_can_message_underling(self, agent_mid, agent_junior):
        assert agent_mid.can_message(agent_junior) is True

    def test_can_message_same_team(self, agent_junior, agent_senior):
        assert agent_junior.can_message(agent_senior) is True

    def test_cannot_message_different_team(self):
        agent_a = Agent(
            id="agent-a",
            name="Agent A",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR,
            team_id="team-1"
        )
        agent_b = Agent(
            id="agent-b",
            name="Agent B",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR,
            team_id="team-2"
        )
        assert agent_a.can_message(agent_b) is False

    def test_cannot_message_no_team(self):
        agent_a = Agent(
            id="agent-a",
            name="Agent A",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR,
            team_id="team-1"
        )
        agent_b = Agent(
            id="agent-b",
            name="Agent B",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR,
            team_id=None
        )
        assert agent_a.can_message(agent_b) is False


class TestGetRoleLevel:
    def test_get_role_level_junior(self, agent_junior):
        assert agent_junior.get_role_level() == 1

    def test_get_role_level_mid(self, agent_mid):
        assert agent_mid.get_role_level() == 2

    def test_get_role_level_senior(self, agent_senior):
        assert agent_senior.get_role_level() == 3

    def test_get_role_level_lead(self, agent_lead):
        assert agent_lead.get_role_level() == 4


class TestGetReportingChain:
    def test_get_reporting_chain_empty(self, agent_junior):
        assert agent_junior.get_reporting_chain() == []

    def test_get_reporting_chain_lead(self, agent_lead):
        assert agent_lead.get_reporting_chain() == []