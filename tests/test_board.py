import pytest
from src.models.board import TicketBoard, Swimlane
from src.models.ticket import Ticket
from src.models.enums import TicketStatus, TicketPriority


class TestTicketBoardCreation:
    def test_board_creation_minimal(self):
        board = TicketBoard(
            id="board-1",
            name="Test Board"
        )
        assert board.id == "board-1"
        assert board.name == "Test Board"
        assert board.team_id is None

    def test_board_creation_with_team(self, ticket_board):
        assert ticket_board.id == "board-1"
        assert ticket_board.name == "Main Board"
        assert ticket_board.team_id == "team-1"


class TestAddSwimlane:
    def test_add_swimlane(self, ticket_board):
        swimlane = ticket_board.add_swimlane("team-2")
        assert swimlane is not None
        assert swimlane.team_id == "team-2"

    def test_add_existing_swimlane_returns_existing(self, ticket_board):
        swimlane1 = ticket_board.add_swimlane("team-2")
        swimlane2 = ticket_board.add_swimlane("team-2")
        assert swimlane1 is swimlane2


class TestRemoveSwimlane:
    def test_remove_swimlane(self, ticket_board):
        ticket_board.add_swimlane("team-2")
        result = ticket_board.remove_swimlane("team-2")
        assert result is True

    def test_remove_nonexistent_swimlane(self, ticket_board):
        result = ticket_board.remove_swimlane("team-nonexistent")
        assert result is False


class TestGetSwimlane:
    def test_get_swimlane_exists(self, ticket_board):
        ticket_board.add_swimlane("team-2")
        swimlane = ticket_board.get_swimlane("team-2")
        assert swimlane is not None

    def test_get_swimlane_not_exists(self, ticket_board):
        swimlane = ticket_board.get_swimlane("team-nonexistent")
        assert swimlane is None


class TestAddTicketToSwimlane:
    def test_add_ticket_to_swimlane(self, ticket_board):
        ticket_board.add_ticket_to_swimlane("team-1", "ticket-1")
        swimlane = ticket_board.get_swimlane("team-1")
        assert "ticket-1" in swimlane.tickets

    def test_add_ticket_creates_swimlane_if_not_exists(self, ticket_board):
        ticket_board.add_ticket_to_swimlane("team-new", "ticket-1")
        swimlane = ticket_board.get_swimlane("team-new")
        assert swimlane is not None

    def test_add_duplicate_ticket_no_duplicate(self, ticket_board):
        ticket_board.add_ticket_to_swimlane("team-1", "ticket-1")
        ticket_board.add_ticket_to_swimlane("team-1", "ticket-1")
        swimlane = ticket_board.get_swimlane("team-1")
        assert swimlane.tickets.count("ticket-1") == 1


class TestRemoveTicketFromSwimlane:
    def test_remove_ticket_from_swimlane(self, ticket_board):
        ticket_board.add_ticket_to_swimlane("team-1", "ticket-1")
        result = ticket_board.remove_ticket_from_swimlane("team-1", "ticket-1")
        assert result is True

    def test_remove_nonexistent_ticket(self, ticket_board):
        result = ticket_board.remove_ticket_from_swimlane("team-1", "ticket-nonexistent")
        assert result is False

    def test_remove_ticket_from_nonexistent_swimlane(self, ticket_board):
        result = ticket_board.remove_ticket_from_swimlane("team-nonexistent", "ticket-1")
        assert result is False


class TestGetTicketsByStatus:
    def test_get_tickets_by_status(self, ticket_board):
        tickets = {
            "ticket-1": Ticket(id="ticket-1", title="Test", status=TicketStatus.BACKLOG),
            "ticket-2": Ticket(id="ticket-2", title="Test", status=TicketStatus.IN_PROGRESS),
            "ticket-3": Ticket(id="ticket-3", title="Test", status=TicketStatus.DONE),
        }
        result = ticket_board.get_tickets_by_status(tickets)
        assert "ticket-1" in result[TicketStatus.BACKLOG]
        assert "ticket-2" in result[TicketStatus.IN_PROGRESS]
        assert "ticket-3" in result[TicketStatus.DONE]


class TestGetSwimlaneTickets:
    def test_get_swimlane_tickets(self, ticket_board):
        ticket_board.add_ticket_to_swimlane("team-1", "ticket-1")
        ticket_board.add_ticket_to_swimlane("team-1", "ticket-2")
        
        tickets = {
            "ticket-1": Ticket(id="ticket-1", title="Test", status=TicketStatus.BACKLOG),
            "ticket-2": Ticket(id="ticket-2", title="Test", status=TicketStatus.IN_PROGRESS),
        }
        result = ticket_board.get_swimlane_tickets("team-1", tickets)
        assert "ticket-1" in result[TicketStatus.BACKLOG]
        assert "ticket-2" in result[TicketStatus.IN_PROGRESS]

    def test_get_swimlane_tickets_nonexistent_swimlane(self, ticket_board):
        tickets = {
            "ticket-1": Ticket(id="ticket-1", title="Test", status=TicketStatus.BACKLOG),
        }
        result = ticket_board.get_swimlane_tickets("team-nonexistent", tickets)
        assert result[TicketStatus.BACKLOG] == []