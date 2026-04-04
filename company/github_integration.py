from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class GitHubIssueState(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class GitHubIssue:
    id: str
    number: int
    title: str
    body: str
    state: GitHubIssueState = GitHubIssueState.OPEN
    labels: list[str] = field(default_factory=list)


@dataclass
class GitHubPullRequest:
    id: str
    number: int
    title: str
    body: str
    state: str = "open"
    issue_number: Optional[int] = None
    merged: bool = False


TICKET_STATUS_TO_LABELS = {
    "backlog": "status:backlog",
    "todo": "status:todo",
    "in_progress": "status:in_progress",
    "review": "status:review",
    "done": "status:done",
}

LABEL_TO_TICKET_STATUS = {v: k for k, v in TICKET_STATUS_TO_LABELS.items()}


PRIORITY_TO_LABELS = {
    "low": "priority:low",
    "medium": "priority:medium",
    "high": "priority:high",
    "critical": "priority:critical",
}

LABEL_TO_PRIORITY = {v: k for k, v in PRIORITY_TO_LABELS.items()}


class GitHubIntegration:
    def __init__(self, repo: str, token: Optional[str] = None):
        self.repo = repo
        self.token = token
        self._issues: dict[int, GitHubIssue] = {}
        self._pull_requests: dict[int, GitHubPullRequest] = {}

    def sync_ticket_to_issue(self, ticket_id: str, issue_number: int) -> GitHubIssue:
        if issue_number in self._issues:
            return self._issues[issue_number]
        issue = GitHubIssue(
            id=ticket_id,
            number=issue_number,
            title=f"Ticket: {ticket_id}",
            body=f"Synced ticket: {ticket_id}",
        )
        self._issues[issue_number] = issue
        return issue

    def update_issue_status(self, issue_number: int, ticket_status: str) -> None:
        if issue_number not in self._issues:
            return
        issue = self._issues[issue_number]
        old_label = self._get_status_label(issue.labels)
        if old_label:
            issue.labels.remove(old_label)
        new_label = TICKET_STATUS_TO_LABELS.get(ticket_status)
        if new_label:
            issue.labels.append(new_label)

    def update_issue_priority(self, issue_number: int, priority: str) -> None:
        if issue_number not in self._issues:
            return
        issue = self._issues[issue_number]
        old_label = self._get_priority_label(issue.labels)
        if old_label:
            issue.labels.remove(old_label)
        new_label = PRIORITY_TO_LABELS.get(priority)
        if new_label:
            issue.labels.append(new_label)

    def _get_status_label(self, labels: list[str]) -> Optional[str]:
        for label in labels:
            if label.startswith("status:"):
                return label
        return None

    def _get_priority_label(self, labels: list[str]) -> Optional[str]:
        for label in labels:
            if label.startswith("priority:"):
                return label
        return None

    def set_issue_closed(self, issue_number: int, merged: bool = False) -> None:
        if issue_number not in self._issues:
            return
        issue = self._issues[issue_number]
        issue.state = GitHubIssueState.CLOSED
        if not merged:
            issue.labels.append("closed:wont_fix" if merged else "closed:completed")

    def link_pr_to_ticket(self, pr_number: int, issue_number: int) -> GitHubPullRequest:
        pr = GitHubPullRequest(
            id=f"pr:{pr_number}",
            number=pr_number,
            title=f"PR #{pr_number}",
            body=f"Linked to issue #{issue_number}",
            issue_number=issue_number,
        )
        self._pull_requests[pr_number] = pr
        return pr

    def mark_pr_merged(self, pr_number: int) -> None:
        if pr_number not in self._pull_requests:
            return
        pr = self._pull_requests[pr_number]
        pr.merged = True
        pr.state = "closed"
        if pr.issue_number and pr.issue_number in self._issues:
            self.set_issue_closed(pr.issue_number, merged=True)

    def get_issue_for_ticket(self, ticket_id: str) -> Optional[GitHubIssue]:
        for issue in self._issues.values():
            if issue.id == ticket_id:
                return issue
        return None

    def get_prs_for_issue(self, issue_number: int) -> list[GitHubPullRequest]:
        return [pr for pr in self._pull_requests.values() if pr.issue_number == issue_number]