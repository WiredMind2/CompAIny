import sqlite3
import json
from datetime import datetime, timezone
from typing import Optional, List
from contextlib import contextmanager

from .models import Agent, Team, Ticket, Meeting, AgentMemory, Role, Level, TeamType, TicketStatus, TicketPriority, MeetingType, MeetingReport


class Database:
    def __init__(self, db_path: str = "company.db"):
        self.db_path = db_path
        self._connection = None
        self.init_schema()

    def _get_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    @contextmanager
    def get_connection(self):
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def init_schema(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    team_id TEXT,
                    boss_id TEXT,
                    short_term TEXT,
                    long_term TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    leader_id TEXT NOT NULL,
                    member_ids TEXT,
                    created_at TEXT,
                    updated_at TEXT
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
                    locked_by TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    participant_ids TEXT,
                    leader_id TEXT,
                    reports TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

    def save_agent(self, agent: Agent):
        now = datetime.now(timezone.utc).isoformat()
        short_term = json.dumps(agent.memory.short_term)
        long_term = json.dumps(agent.memory.long_term)
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agents 
                (id, role, level, team_id, boss_id, short_term, long_term, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM agents WHERE id = ?), ?), ?)
            """, (
                agent.id, agent.role.value, agent.level.value, agent.team_id,
                agent.boss_id, short_term, long_term, agent.id, now, now
            ))

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
            if not row:
                return None
            return self._row_to_agent(row)

    def get_all_agents(self) -> List[Agent]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM agents").fetchall()
            return [self._row_to_agent(row) for row in rows]

    def _row_to_agent(self, row) -> Agent:
        memory = AgentMemory(
            short_term=json.loads(row["short_term"] or "{}"),
            long_term=json.loads(row["long_term"] or "[]")
        )
        return Agent(
            id=row["id"],
            role=Role(row["role"]),
            level=Level(row["level"]),
            team_id=row["team_id"],
            boss_id=row["boss_id"],
            memory=memory
        )

    def save_team(self, team: Team):
        now = datetime.now(timezone.utc).isoformat()
        member_ids = json.dumps(team.member_ids)
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO teams 
                (id, type, leader_id, member_ids, created_at, updated_at)
                VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM teams WHERE id = ?), ?), ?)
            """, (
                team.id, team.type.value, team.leader_id, member_ids, team.id, now, now
            ))

    def get_team(self, team_id: str) -> Optional[Team]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
            if not row:
                return None
            return self._row_to_team(row)

    def get_all_teams(self) -> List[Team]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM teams").fetchall()
            return [self._row_to_team(row) for row in rows]

    def _row_to_team(self, row) -> Team:
        return Team(
            id=row["id"],
            type=TeamType(row["type"]),
            leader_id=row["leader_id"],
            member_ids=json.loads(row["member_ids"] or "[]")
        )

    def save_ticket(self, ticket: Ticket):
        now = datetime.now(timezone.utc).isoformat()
        subtasks = json.dumps(ticket.subtasks)
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tickets 
                (id, status, priority, assignee_id, github_issue_id, subtasks, complexity, locked_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM tickets WHERE id = ?), ?), ?)
            """, (
                ticket.id, ticket.status.value, ticket.priority.value,
                ticket.assignee_id, ticket.github_issue_id, subtasks,
                ticket.complexity, ticket.locked_by, ticket.id, now, now
            ))

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
            if not row:
                return None
            return self._row_to_ticket(row)

    def get_all_tickets(self) -> List[Ticket]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM tickets").fetchall()
            return [self._row_to_ticket(row) for row in rows]

    def _row_to_ticket(self, row) -> Ticket:
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

    def save_meeting(self, meeting: Meeting):
        now = datetime.now(timezone.utc).isoformat()
        participant_ids = json.dumps(meeting.participant_ids)
        reports = json.dumps([{"author_id": r.author_id, "content": r.content} for r in meeting.reports])
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO meetings 
                (id, type, participant_ids, leader_id, reports, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM meetings WHERE id = ?), ?), ?)
            """, (
                meeting.id, meeting.type.value, participant_ids, meeting.leader_id,
                reports, meeting.id, now, now
            ))

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,)).fetchone()
            if not row:
                return None
            return self._row_to_meeting(row)

    def get_all_meetings(self) -> List[Meeting]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM meetings").fetchall()
            return [self._row_to_meeting(row) for row in rows]

    def _row_to_meeting(self, row) -> Meeting:
        reports_data = json.loads(row["reports"] or "[]")
        reports = [MeetingReport(author_id=r["author_id"], content=r["content"]) for r in reports_data]
        return Meeting(
            id=row["id"],
            type=MeetingType(row["type"]),
            participant_ids=json.loads(row["participant_ids"] or "[]"),
            leader_id=row["leader_id"],
            reports=reports
        )

    def delete_agent(self, agent_id: str):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM agents WHERE id = ?", (agent_id,))

    def delete_team(self, team_id: str):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM teams WHERE id = ?", (team_id,))

    def delete_ticket(self, ticket_id: str):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))

    def delete_meeting(self, meeting_id: str):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))


class MemoryStore:
    def __init__(self, db: Database):
        self.db = db

    def update_short_term(self, agent_id: str, key: str, value):
        agent = self.db.get_agent(agent_id)
        if agent:
            agent.memory.short_term[key] = value
            self.db.save_agent(agent)

    def get_short_term(self, agent_id: str, key: str):
        agent = self.db.get_agent(agent_id)
        return agent.memory.short_term.get(key) if agent else None

    def add_long_term(self, agent_id: str, memory: str):
        agent = self.db.get_agent(agent_id)
        if agent:
            agent.memory.long_term.append({"timestamp": datetime.now(timezone.utc).isoformat(), "memory": memory})
            self.db.save_agent(agent)

    def get_long_term(self, agent_id: str) -> List[dict]:
        agent = self.db.get_agent(agent_id)
        return agent.memory.long_term if agent else []

    def clear_short_term(self, agent_id: str):
        agent = self.db.get_agent(agent_id)
        if agent:
            agent.memory.short_term = {}
            self.db.save_agent(agent)