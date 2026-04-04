import os
import unittest

from company import Database, MemoryStore, Agent, Team, Ticket, Meeting, Role, Level, TeamType, TicketStatus, TicketPriority, MeetingType


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def test_save_and_get_agent(self):
        agent = Agent(id="agent1", role=Role.DEVELOPER, level=Level.L3)
        self.db.save_agent(agent)
        
        retrieved = self.db.get_agent("agent1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "agent1")
        self.assertEqual(retrieved.role, Role.DEVELOPER)
        self.assertEqual(retrieved.level, Level.L3)

    def test_save_agent_with_memory(self):
        agent = Agent(id="agent1", role=Role.DEVELOPER, level=Level.L3)
        agent.memory.short_term["current_task"] = "Writing tests"
        agent.memory.long_term.append({"memory": "Learned Python", "timestamp": "2026-01-01"})
        self.db.save_agent(agent)
        
        retrieved = self.db.get_agent("agent1")
        self.assertEqual(retrieved.memory.short_term["current_task"], "Writing tests")
        self.assertEqual(len(retrieved.memory.long_term), 1)
        self.assertEqual(retrieved.memory.long_term[0]["memory"], "Learned Python")

    def test_get_all_agents(self):
        self.db.save_agent(Agent(id="a1", role=Role.DEVELOPER, level=Level.L1))
        self.db.save_agent(Agent(id="a2", role=Role.PO, level=Level.L5))
        
        agents = self.db.get_all_agents()
        self.assertEqual(len(agents), 2)

    def test_save_and_get_team(self):
        team = Team(id="team1", type=TeamType.ENGINEERING, leader_id="agent1", member_ids=["agent1", "agent2"])
        self.db.save_team(team)
        
        retrieved = self.db.get_team("team1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.type, TeamType.ENGINEERING)
        self.assertEqual(len(retrieved.member_ids), 2)

    def test_save_and_get_ticket(self):
        ticket = Ticket(id="ticket1", status=TicketStatus.IN_PROGRESS, priority=TicketPriority.HIGH, complexity=5)
        self.db.save_ticket(ticket)
        
        retrieved = self.db.get_ticket("ticket1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.status, TicketStatus.IN_PROGRESS)
        self.assertEqual(retrieved.complexity, 5)

    def test_save_and_get_meeting(self):
        meeting = Meeting(id="meet1", type=MeetingType.DAILY_STANDUP, leader_id="agent1")
        meeting.add_report("agent1", "Progress: working on tests")
        self.db.save_meeting(meeting)
        
        retrieved = self.db.get_meeting("meet1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved.reports), 1)
        self.assertEqual(retrieved.reports[0].content, "Progress: working on tests")

    def test_delete_operations(self):
        self.db.save_agent(Agent(id="a1", role=Role.DEVELOPER, level=Level.L1))
        self.db.delete_agent("a1")
        self.assertIsNone(self.db.get_agent("a1"))

    def test_update_existing(self):
        agent = Agent(id="a1", role=Role.DEVELOPER, level=Level.L1)
        self.db.save_agent(agent)
        
        agent.level = Level.L2
        self.db.save_agent(agent)
        
        retrieved = self.db.get_agent("a1")
        self.assertEqual(retrieved.level, Level.L2)


class TestMemoryStore(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.store = MemoryStore(self.db)
        self.db.save_agent(Agent(id="agent1", role=Role.DEVELOPER, level=Level.L3))

    def test_update_short_term(self):
        self.store.update_short_term("agent1", "task", "coding")
        result = self.store.get_short_term("agent1", "task")
        self.assertEqual(result, "coding")

    def test_add_long_term(self):
        self.store.add_long_term("agent1", "Completed project X")
        memories = self.store.get_long_term("agent1")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0]["memory"], "Completed project X")

    def test_clear_short_term(self):
        self.store.update_short_term("agent1", "task", "coding")
        self.store.clear_short_term("agent1")
        result = self.store.get_short_term("agent1", "task")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()