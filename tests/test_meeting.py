import pytest
from src.models.meeting import Meeting, MeetingType


class TestMeetingCreation:
    def test_meeting_creation_minimal(self):
        meeting = Meeting(
            id="meeting-1",
            type=MeetingType.STANDUP,
            team_id="team-1",
            host_id="agent-1"
        )
        assert meeting.id == "meeting-1"
        assert meeting.type == MeetingType.STANDUP
        assert meeting.team_id == "team-1"
        assert meeting.host_id == "agent-1"

    def test_meeting_creation_full(self, meeting_standup):
        assert meeting_standup.id == "meeting-1"
        assert meeting_standup.type == MeetingType.STANDUP
        assert meeting_standup.team_id == "team-1"
        assert meeting_standup.host_id == "agent-4"
        assert "agent-1" in meeting_standup.participant_ids


class TestAddParticipant:
    def test_add_participant(self, meeting_standup):
        meeting_standup.add_participant("agent-new")
        assert "agent-new" in meeting_standup.participant_ids

    def test_add_existing_participant_no_duplicate(self, meeting_standup):
        meeting_standup.add_participant("agent-1")
        meeting_standup.add_participant("agent-1")
        assert meeting_standup.participant_ids.count("agent-1") == 1


class TestRemoveParticipant:
    def test_remove_participant(self, meeting_standup):
        result = meeting_standup.remove_participant("agent-1")
        assert result is True
        assert "agent-1" not in meeting_standup.participant_ids

    def test_remove_nonexistent_participant(self, meeting_standup):
        result = meeting_standup.remove_participant("agent-nonexistent")
        assert result is False


class TestAddReport:
    def test_add_report(self, meeting_standup):
        meeting_standup.add_report("Test report content")
        assert "Test report content" in meeting_standup.reports


class TestComplete:
    def test_complete_meeting(self, meeting_standup):
        meeting_standup.complete()
        assert meeting_standup.completed_at is not None