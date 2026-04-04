import sqlite3
import json
from pathlib import Path
from typing import Optional, Any
from contextlib import contextmanager

from .models import Agent, Team, Ticket, AgentMemory, Role, Level, TicketStatus, TicketPriority, TeamType


class Database:
    def __init__(self, db_path: str = "company.db"):
        self.db_path = db_path
        self._connection = None
        if db_path == ":memory:":
            self._connection = sqlite3.connect(db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        conn = self._connection or sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    team_id TEXT,
                    boss_id TEXT,
                    memory_short_term TEXT,
                    memory_long_term TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    leader_id TEXT NOT NULL,
                    member_ids TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    assignee_id TEXT,
                    github_issue_id TEXT,
                    subtasks TEXT,
                    complexity INTEGER,
                    locked_by TEXT
                )
            """)
            conn.commit()
        finally:
            if not self._connection:
                conn.close()

    @contextmanager
    def get_connection(self):
        if self._connection:
            yield self._connection
            self._connection.commit()
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def save_agent(self, agent: Agent) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agents 
                (id, role, level, team_id, boss_id, memory_short_term, memory_long_term)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                agent.id,
                agent.role.value,
                agent.level.value,
                agent.team_id,
                agent.boss_id,
                json.dumps(agent.memory.short_term),
                json.dumps(agent.memory.long_term)
            ))

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
            if not row:
                return None
            return self._row_to_agent(row)

    def get_all_agents(self) -> list[Agent]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM agents").fetchall()
            return [self._row_to_agent(row) for row in rows]

    def delete_agent(self, agent_id: str) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM agents WHERE id = ?", (agent_id,))

    def _row_to_agent(self, row: sqlite3.Row) -> Agent:
        memory = AgentMemory(
            short_term=json.loads(row["memory_short_term"] or "{}"),
            long_term=json.loads(row["memory_long_term"] or "[]")
        )
        return Agent(
            id=row["id"],
            role=Role(row["role"]),
            level=Level(row["level"]),
            team_id=row["team_id"],
            boss_id=row["boss_id"],
            memory=memory
        )

    def save_team(self, team: Team) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO teams (id, type, leader_id, member_ids)
                VALUES (?, ?, ?, ?)
            """, (
                team.id,
                team.type.value,
                team.leader_id,
                json.dumps(team.member_ids)
            ))

    def get_team(self, team_id: str) -> Optional[Team]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
            if not row:
                return None
            return self._row_to_team(row)

    def get_all_teams(self) -> list[Team]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM teams").fetchall()
            return [self._row_to_team(row) for row in rows]

    def delete_team(self, team_id: str) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM teams WHERE id = ?", (team_id,))

    def _row_to_team(self, row: sqlite3.Row) -> Team:
        return Team(
            id=row["id"],
            type=TeamType(row["type"]),
            leader_id=row["leader_id"],
            member_ids=json.loads(row["member_ids"] or "[]")
        )

    def save_ticket(self, ticket: Ticket) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tickets 
                (id, status, priority, assignee_id, github_issue_id, subtasks, complexity, locked_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket.id,
                ticket.status.value,
                ticket.priority.value,
                ticket.assignee_id,
                ticket.github_issue_id,
                json.dumps(ticket.subtasks),
                ticket.complexity,
                ticket.locked_by
            ))

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
            if not row:
                return None
            return self._row_to_ticket(row)

    def get_all_tickets(self) -> list[Ticket]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM tickets").fetchall()
            return [self._row_to_ticket(row) for row in rows]

    def get_tickets_by_status(self, status: TicketStatus) -> list[Ticket]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM tickets WHERE status = ?", (status.value,)).fetchall()
            return [self._row_to_ticket(row) for row in rows]

    def delete_ticket(self, ticket_id: str) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))

    def _row_to_ticket(self, row: sqlite3.Row) -> Ticket:
        return Ticket(
            id=row["id"],
            status=TicketStatus(row["status"]),
            priority=TicketPriority(row["priority"]),
            assignee_id=row["assignee_id"],
            github_issue_id=row["github_issue_id"],
            subtasks=json.loads(row["subtasks"] or "[]"),
            complexity=row["complexity"],
            locked_by=row["locked_by"]
        )