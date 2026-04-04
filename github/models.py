from enum import Enum
from typing import Optional, List


class TicketStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


GITHUB_STATUS_LABELS = {
    "backlog": ["backlog", "wontfix", "enhancement"],
    "todo": ["todo", "ready", "priority"],
    "in_progress": ["in-progress", "doing", "working"],
    "review": ["review", "pr", "reviewer"],
    "done": ["done", "fixed", "released"],
}


class GitHubIssue:
    def __init__(
        self,
        issue_id: int,
        title: str,
        body: str = "",
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        state: str = "open",
    ):
        self.issue_id = issue_id
        self.title = title
        self.body = body
        self.labels = labels or []
        self.assignee = assignee
        self.state = state

    def get_status(self) -> Optional[TicketStatus]:
        for status, label_names in GITHUB_STATUS_LABELS.items():
            for label in self.labels:
                if label.lower() in [l.lower() for l in label_names]:
                    return TicketStatus(status)
        return None

    def to_dict(self) -> dict:
        return {
            "issue_id": self.issue_id,
            "title": self.title,
            "body": self.body,
            "labels": self.labels,
            "assignee": self.assignee,
            "state": self.state,
        }


class GitHubPullRequest:
    def __init__(
        self,
        pr_id: int,
        title: str,
        body: str = "",
        state: str = "open",
        issue_id: Optional[int] = None,
        merged: bool = False,
    ):
        self.pr_id = pr_id
        self.title = title
        self.body = body
        self.state = state
        self.issue_id = issue_id
        self.merged = merged

    def to_dict(self) -> dict:
        return {
            "pr_id": self.pr_id,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "issue_id": self.issue_id,
            "merged": self.merged,
        }