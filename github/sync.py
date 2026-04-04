from typing import Optional, List, Dict, Any
import logging

from .models import GitHubIssue, GitHubPullRequest, TicketStatus
from models.ticket import Ticket


logger = logging.getLogger(__name__)


class GitHubSync:
    def __init__(self, repo: str, token: Optional[str] = None):
        self.repo = repo
        self.token = token

    def sync_issue_to_ticket(self, issue: GitHubIssue) -> Dict[str, Any]:
        status = issue.get_status()
        return {
            "title": issue.title,
            "description": issue.body,
            "status": status.value if status else TicketStatus.BACKLOG.value,
            "assignee_id": issue.assignee,
            "github_issue_id": issue.issue_id,
            "labels": issue.labels,
        }

    def sync_ticket_to_issue(self, ticket: Ticket) -> GitHubIssue:
        labels = [ticket.status.value]
        if ticket.priority.value != "medium":
            labels.append(ticket.priority.value)
        return GitHubIssue(
            issue_id=ticket.github_issue_id or 0,
            title=ticket.title,
            body=ticket.description,
            labels=labels,
            assignee=ticket.assignee_id,
            state="closed" if ticket.status == TicketStatus.DONE else "open",
        )

    def link_pr_to_ticket(self, pr: GitHubPullRequest, ticket: Ticket) -> None:
        if pr.issue_id:
            ticket.github_issue_id = pr.issue_id
        if pr.pr_id:
            ticket.link_pr(pr.pr_id)
        if pr.merged and ticket.status != TicketStatus.DONE:
            ticket.status = TicketStatus.DONE
        logger.info(f"Linked PR {pr.pr_id} to ticket {ticket.id}")

    def get_issue_labels(self, issue: GitHubIssue) -> List[str]:
        return issue.labels

    def map_status_to_labels(self, status: TicketStatus) -> List[str]:
        return [status.value]

    def update_issue_status(self, issue: GitHubIssue, status: TicketStatus) -> GitHubIssue:
        new_labels = [status.value]
        current_status = issue.get_status()
        existing = [l for l in issue.labels if l != (current_status.value if current_status else None)]
        new_labels.extend(existing)
        return GitHubIssue(
            issue_id=issue.issue_id,
            title=issue.title,
            body=issue.body,
            labels=new_labels,
            assignee=issue.assignee,
            state="closed" if status == TicketStatus.DONE else "open",
        )