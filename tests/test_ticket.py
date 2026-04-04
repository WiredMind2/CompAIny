import pytest
from src.models.ticket import Ticket, Subtask
from src.models.enums import TicketStatus, TicketPriority


class TestTicketCreation:
    def test_ticket_creation_minimal(self):
        ticket = Ticket(
            id="ticket-1",
            title="Test Ticket"
        )
        assert ticket.id == "ticket-1"
        assert ticket.title == "Test Ticket"
        assert ticket.status == TicketStatus.BACKLOG
        assert ticket.priority == TicketPriority.MEDIUM

    def test_ticket_creation_full(self, ticket_backlog):
        assert ticket_backlog.id == "ticket-1"
        assert ticket_backlog.title == "Test Ticket"
        assert ticket_backlog.description == "A test ticket"
        assert ticket_backlog.status == TicketStatus.BACKLOG
        assert ticket_backlog.priority == TicketPriority.MEDIUM
        assert ticket_backlog.assignee_id == "agent-1"
        assert ticket_backlog.team_id == "team-1"


class TestIsLocked:
    def test_is_locked_false_by_default(self, ticket_backlog):
        assert ticket_backlog.is_locked() is False

    def test_is_locked_true_when_locked(self, ticket_backlog):
        ticket_backlog.lock("agent-1")
        assert ticket_backlog.is_locked() is True


class TestLock:
    def test_lock_ticket(self, ticket_backlog):
        result = ticket_backlog.lock("agent-1")
        assert result is True
        assert ticket_backlog.locked_by == "agent-1"
        assert ticket_backlog.locked_at is not None

    def test_lock_already_locked_ticket(self, ticket_backlog):
        ticket_backlog.lock("agent-1")
        result = ticket_backlog.lock("agent-2")
        assert result is False
        assert ticket_backlog.locked_by == "agent-1"


class TestUnlock:
    def test_unlock_ticket(self, ticket_backlog):
        ticket_backlog.lock("agent-1")
        result = ticket_backlog.unlock("agent-1")
        assert result is True
        assert ticket_backlog.locked_by is None
        assert ticket_backlog.locked_at is None

    def test_unlock_not_owner(self, ticket_backlog):
        ticket_backlog.lock("agent-1")
        result = ticket_backlog.unlock("agent-2")
        assert result is False
        assert ticket_backlog.locked_by == "agent-1"

    def test_unlock_not_locked(self, ticket_backlog):
        result = ticket_backlog.unlock("agent-1")
        assert result is False


class TestAssign:
    def test_assign_ticket(self, ticket_backlog):
        ticket_backlog.assign("agent-2")
        assert ticket_backlog.assignee_id == "agent-2"

    def test_assign_updates_updated_at(self, ticket_backlog):
        original_updated = ticket_backlog.updated_at
        ticket_backlog.assign("agent-2")
        assert ticket_backlog.updated_at >= original_updated


class TestSetStatus:
    def test_set_status(self, ticket_backlog):
        ticket_backlog.set_status(TicketStatus.IN_PROGRESS)
        assert ticket_backlog.status == TicketStatus.IN_PROGRESS

    def test_set_status_to_done_sets_completed_at(self, ticket_backlog):
        ticket_backlog.set_status(TicketStatus.DONE)
        assert ticket_backlog.completed_at is not None


class TestSetPriority:
    def test_set_priority(self, ticket_backlog):
        ticket_backlog.set_priority(TicketPriority.HIGH)
        assert ticket_backlog.priority == TicketPriority.HIGH


class TestAddSubtask:
    def test_add_subtask(self, ticket_backlog):
        subtask = ticket_backlog.add_subtask("Test subtask")
        assert subtask.id == "ticket-1-subtask-1"
        assert subtask.title == "Test subtask"
        assert subtask.completed is False

    def test_add_multiple_subtasks(self, ticket_backlog):
        ticket_backlog.add_subtask("Subtask 1")
        subtask = ticket_backlog.add_subtask("Subtask 2")
        assert subtask.id == "ticket-1-subtask-2"


class TestCompleteSubtask:
    def test_complete_subtask(self, ticket_backlog):
        subtask = ticket_backlog.add_subtask("Test subtask")
        result = ticket_backlog.complete_subtask(subtask.id)
        assert result is True
        assert subtask.completed is True

    def test_complete_nonexistent_subtask(self, ticket_backlog):
        result = ticket_backlog.complete_subtask("nonexistent")
        assert result is False


class TestGetSubtaskProgress:
    def test_get_subtask_progress_empty(self, ticket_backlog):
        completed, total = ticket_backlog.get_subtask_progress()
        assert completed == 0
        assert total == 0

    def test_get_subtask_progress_with_subtasks(self, ticket_backlog):
        ticket_backlog.add_subtask("Subtask 1")
        ticket_backlog.add_subtask("Subtask 2")
        subtask = ticket_backlog.add_subtask("Subtask 3")
        ticket_backlog.complete_subtask(subtask.id)
        
        completed, total = ticket_backlog.get_subtask_progress()
        assert completed == 1
        assert total == 3