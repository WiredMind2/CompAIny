from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from github.models import GitHubIssue, GitHubPullRequest, TicketStatus


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Ticket:
    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        status: TicketStatus = TicketStatus.BACKLOG,
        priority: Priority = Priority.MEDIUM,
        assignee_id: Optional[str] = None,
        github_issue_id: Optional[int] = None,
        subtasks: Optional[List[str]] = None,
        complexity: int = 1,
        locked_by: Optional[str] = None,
        team_id: Optional[str] = None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.assignee_id = assignee_id
        self.github_issue_id = github_issue_id
        self.subtasks = subtasks or []
        self.complexity = complexity
        self.locked_by = locked_by
        self.team_id = team_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.linked_prs: List[int] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assignee_id": self.assignee_id,
            "github_issue_id": self.github_issue_id,
            "subtasks": self.subtasks,
            "complexity": self.complexity,
            "locked_by": self.locked_by,
            "team_id": self.team_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "linked_prs": self.linked_prs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        ticket = cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TicketStatus(data.get("status", "backlog")),
            priority=Priority(data.get("priority", "medium")),
            assignee_id=data.get("assignee_id"),
            github_issue_id=data.get("github_issue_id"),
            subtasks=data.get("subtasks", []),
            complexity=data.get("complexity", 1),
            locked_by=data.get("locked_by"),
            team_id=data.get("team_id"),
        )
        ticket.linked_prs = data.get("linked_prs", [])
        if "created_at" in data:
            ticket.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            ticket.updated_at = datetime.fromisoformat(data["updated_at"])
        return ticket

    def link_github_issue(self, issue_id: int) -> None:
        self.github_issue_id = issue_id
        self.updated_at = datetime.utcnow()

    def link_pr(self, pr_id: int) -> None:
        if pr_id not in self.linked_prs:
            self.linked_prs.append(pr_id)
            self.updated_at = datetime.utcnow()

    def sync_from_github(self, issue: GitHubIssue) -> None:
        if issue.title:
            self.title = issue.title
        if issue.body:
            self.description = issue.body
        status = issue.get_status()
        if status:
            self.status = status
        if issue.assignee:
            self.assignee_id = issue.assignee
        self.updated_at = datetime.utcnow()

    def to_github_issue(self) -> GitHubIssue:
        labels = [self.status.value]
        if self.priority != Priority.MEDIUM:
            labels.append(self.priority.value)
        return GitHubIssue(
            issue_id=self.github_issue_id or 0,
            title=self.title,
            body=self.description,
            labels=labels,
            assignee=self.assignee_id,
            state="open" if self.status != TicketStatus.DONE else "closed",
        )