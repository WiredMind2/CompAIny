import pytest
from src.models.team import Team
from src.models.enums import TeamType


class TestTeamCreation:
    def test_team_creation_minimal(self):
        team = Team(
            id="team-1",
            name="Test Team",
            type=TeamType.ENGINEERING,
            leader_id="agent-lead"
        )
        assert team.id == "team-1"
        assert team.name == "Test Team"
        assert team.type == TeamType.ENGINEERING
        assert team.leader_id == "agent-lead"

    def test_team_creation_full(self, team_engineering):
        assert team_engineering.id == "team-1"
        assert team_engineering.name == "Engineering Team"
        assert team_engineering.type == TeamType.ENGINEERING
        assert team_engineering.leader_id == "agent-4"
        assert "agent-1" in team_engineering.member_ids


class TestAddMember:
    def test_add_member(self, team_engineering):
        team_engineering.add_member("agent-new")
        assert "agent-new" in team_engineering.member_ids

    def test_add_existing_member_no_duplicate(self, team_engineering):
        team_engineering.add_member("agent-1")
        team_engineering.add_member("agent-1")
        assert team_engineering.member_ids.count("agent-1") == 1


class TestRemoveMember:
    def test_remove_member(self, team_engineering):
        team_engineering.remove_member("agent-1")
        assert "agent-1" not in team_engineering.member_ids

    def test_remove_nonexistent_member(self, team_engineering):
        team_engineering.remove_member("agent-nonexistent")
        assert "agent-nonexistent" not in team_engineering.member_ids


class TestAddSubteam:
    def test_add_subteam(self, team_engineering):
        team_engineering.add_subteam("subteam-1")
        assert "subteam-1" in team_engineering.subteam_ids

    def test_add_existing_subteam_no_duplicate(self, team_engineering):
        team_engineering.add_subteam("subteam-1")
        team_engineering.add_subteam("subteam-1")
        assert team_engineering.subteam_ids.count("subteam-1") == 1


class TestRemoveSubteam:
    def test_remove_subteam(self, team_engineering):
        team_engineering.add_subteam("subteam-1")
        team_engineering.remove_subteam("subteam-1")
        assert "subteam-1" not in team_engineering.subteam_ids

    def test_remove_nonexistent_subteam(self, team_engineering):
        team_engineering.remove_subteam("subteam-nonexistent")
        assert "subteam-nonexistent" not in team_engineering.subteam_ids


class TestIsLeader:
    def test_is_leader_true(self, team_engineering):
        assert team_engineering.is_leader("agent-4") is True

    def test_is_leader_false(self, team_engineering):
        assert team_engineering.is_leader("agent-1") is False


class TestGetAllMemberIds:
    def test_get_all_member_ids(self, team_engineering):
        member_ids = team_engineering.get_all_member_ids()
        assert "agent-1" in member_ids
        assert "agent-2" in member_ids
        assert "agent-3" in member_ids