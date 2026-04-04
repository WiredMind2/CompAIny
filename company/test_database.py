import os
import unittest
from company import Database, Agent, Team, Ticket, Role, Level, TeamType, TicketStatus, TicketPriority, AgentMemory


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def test_save_and_get_agent(self):
        agent = Agent(
            id="agent-1",
            role=Role.DEVELOPER,
            level=Level.L3,
            boss_id="agent-0",
            memory=AgentMemory(
                short_term={"current_task": "implementing feature"},
                long_term=["project-alpha", "project-beta"]
            )
        )
        self.db.save_agent(agent)
        
        retrieved = self.db.get_agent("agent-1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "agent-1")
        self.assertEqual(retrieved.role, Role.DEVELOPER)
        self.assertEqual(retrieved.level, Level.L3)
        self.assertEqual(retrieved.boss_id, "agent-0")
        self.assertEqual(retrieved.memory.short_term["current_task"], "implementing feature")
        self.assertEqual(retrieved.memory.long_term, ["project-alpha", "project-beta"])

    def test_get_all_agents(self):
        agent1 = Agent(id="agent-1", role=Role.DEVELOPER, level=Level.L1)
        agent2 = Agent(id="agent-2", role=Role.PO, level=Level.L5)
        self.db.save_agent(agent1)
        self.db.save_agent(agent2)
        
        agents = self.db.get_all_agents()
        self.assertEqual(len(agents), 2)

    def test_delete_agent(self):
        agent = Agent(id="agent-1", role=Role.DEVELOPER, level=Level.L1)
        self.db.save_agent(agent)
        self.db.delete_agent("agent-1")
        
        retrieved = self.db.get_agent("agent-1")
        self.assertIsNone(retrieved)

    def test_save_and_get_team(self):
        team = Team(
            id="team-1",
            type=TeamType.ENGINEERING,
            leader_id="agent-1",
            member_ids=["agent-1", "agent-2"]
        )
        self.db.save_team(team)
        
        retrieved = self.db.get_team("team-1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "team-1")
        self.assertEqual(retrieved.type, TeamType.ENGINEERING)
        self.assertEqual(retrieved.leader_id, "agent-1")
        self.assertEqual(retrieved.member_ids, ["agent-1", "agent-2"])

    def test_get_all_teams(self):
        team1 = Team(id="team-1", type=TeamType.PRODUCT, leader_id="agent-1")
        team2 = Team(id="team-2", type=TeamType.ENGINEERING, leader_id="agent-2")
        self.db.save_team(team1)
        self.db.save_team(team2)
        
        teams = self.db.get_all_teams()
        self.assertEqual(len(teams), 2)

    def test_delete_team(self):
        team = Team(id="team-1", type=TeamType.PRODUCT, leader_id="agent-1")
        self.db.save_team(team)
        self.db.delete_team("team-1")
        
        retrieved = self.db.get_team("team-1")
        self.assertIsNone(retrieved)

    def test_save_and_get_ticket(self):
        ticket = Ticket(
            id="ticket-1",
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.HIGH,
            assignee_id="agent-1",
            subtasks=["subtask-1", "subtask-2"],
            complexity=5,
            locked_by="agent-1"
        )
        self.db.save_ticket(ticket)
        
        retrieved = self.db.get_ticket("ticket-1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "ticket-1")
        self.assertEqual(retrieved.status, TicketStatus.IN_PROGRESS)
        self.assertEqual(retrieved.priority, TicketPriority.HIGH)
        self.assertEqual(retrieved.assignee_id, "agent-1")
        self.assertEqual(retrieved.subtasks, ["subtask-1", "subtask-2"])
        self.assertEqual(retrieved.complexity, 5)
        self.assertEqual(retrieved.locked_by, "agent-1")

    def test_get_all_tickets(self):
        ticket1 = Ticket(id="ticket-1", status=TicketStatus.TODO)
        ticket2 = Ticket(id="ticket-2", status=TicketStatus.DONE)
        self.db.save_ticket(ticket1)
        self.db.save_ticket(ticket2)
        
        tickets = self.db.get_all_tickets()
        self.assertEqual(len(tickets), 2)

    def test_get_tickets_by_status(self):
        ticket1 = Ticket(id="ticket-1", status=TicketStatus.TODO)
        ticket2 = Ticket(id="ticket-2", status=TicketStatus.DONE)
        ticket3 = Ticket(id="ticket-3", status=TicketStatus.TODO)
        self.db.save_ticket(ticket1)
        self.db.save_ticket(ticket2)
        self.db.save_ticket(ticket3)
        
        todo_tickets = self.db.get_tickets_by_status(TicketStatus.TODO)
        self.assertEqual(len(todo_tickets), 2)

    def test_delete_ticket(self):
        ticket = Ticket(id="ticket-1", status=TicketStatus.BACKLOG)
        self.db.save_ticket(ticket)
        self.db.delete_ticket("ticket-1")
        
        retrieved = self.db.get_ticket("ticket-1")
        self.assertIsNone(retrieved)


if __name__ == "__main__":
    unittest.main()