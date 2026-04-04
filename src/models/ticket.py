from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field

from .enums import TicketStatus, TicketPriority


@dataclass
class Subtask:
    id: str
    title: str
    completed: bool = False
    assignee_id: Optional[str] = None


@dataclass
class Ticket:
    id: str
    title: str
    description: str = ""
    status: TicketStatus = TicketStatus.BACKLOG
    priority: TicketPriority = TicketPriority.MEDIUM
    assignee_id: Optional[str] = None
    team_id: Optional[str] = None
    reporter_id: Optional[str] = None
    subtasks: List[Subtask] = field(default_factory=list)
    complexity_estimate: Optional[int] = None
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    parent_ticket_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def is_locked(self) -> bool:
        return self.locked_by is not None

    def lock(self, agent_id: str) -> bool:
        if self.is_locked():
            return False
        self.locked_by = agent_id
        self.locked_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True

    def unlock(self, agent_id: str) -> bool:
        if self.locked_by != agent_id:
            return False
        self.locked_by = None
        self.locked_at = None
        self.updated_at = datetime.utcnow()
        return True

    def assign(self, agent_id: str) -> None:
        self.assignee_id = agent_id
        self.updated_at = datetime.utcnow()

    def set_status(self, status: TicketStatus) -> None:
        self.status = status
        self.updated_at = datetime.utcnow()
        if status == TicketStatus.DONE:
            self.completed_at = datetime.utcnow()

    def set_priority(self, priority: TicketPriority) -> None:
        self.priority = priority
        self.updated_at = datetime.utcnow()

    def add_subtask(self, title: str) -> Subtask:
        subtask = Subtask(
            id=f"{self.id}-subtask-{len(self.subtasks) + 1}",
            title=title
        )
        self.subtasks.append(subtask)
        self.updated_at = datetime.utcnow()
        return subtask

    def complete_subtask(self, subtask_id: str) -> bool:
        for subtask in self.subtasks:
            if subtask.id == subtask_id:
                subtask.completed = True
                self.updated_at = datetime.utcnow()
                return True
        return False

    def get_subtask_progress(self) -> tuple[int, int]:
        if not self.subtasks:
            return 0, 0
        completed = sum(1 for s in self.subtasks if s.completed)
        return completed, len(self.subtasks)