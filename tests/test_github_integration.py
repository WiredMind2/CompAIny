import pytest
from company.github_integration import (
    GitHubIntegration,
    GitHubIssue,
    GitHubPullRequest,
    GitHubIssueState,
    TICKET_STATUS_TO_LABELS,
    PRIORITY_TO_LABELS,
    LABEL_TO_TICKET_STATUS,
    LABEL_TO_PRIORITY,
)


class TestGitHubIssueCreation:
    def test_github_issue_creation_minimal(self):
        issue = GitHubIssue(
            id="issue-1",
            number=1,
            title="Test Issue",
            body="Issue body"
        )
        assert issue.id == "issue-1"
        assert issue.number == 1
        assert issue.title == "Test Issue"
        assert issue.body == "Issue body"
        assert issue.state == GitHubIssueState.OPEN
        assert issue.labels == []

    def test_github_issue_creation_full(self):
        issue = GitHubIssue(
            id="issue-1",
            number=1,
            title="Test Issue",
            body="Issue body",
            state=GitHubIssueState.CLOSED,
            labels=["bug", "priority:high"]
        )
        assert issue.state == GitHubIssueState.CLOSED
        assert issue.labels == ["bug", "priority:high"]


class TestGitHubPullRequestCreation:
    def test_github_pr_creation_minimal(self):
        pr = GitHubPullRequest(
            id="pr-1",
            number=1,
            title="Test PR",
            body="PR body"
        )
        assert pr.id == "pr-1"
        assert pr.number == 1
        assert pr.state == "open"
        assert pr.merged is False

    def test_github_pr_creation_full(self):
        pr = GitHubPullRequest(
            id="pr-1",
            number=1,
            title="Test PR",
            body="PR body",
            state="closed",
            issue_number=123,
            merged=True
        )
        assert pr.issue_number == 123
        assert pr.merged is True


class TestLabelMappings:
    def test_ticket_status_to_labels(self):
        assert TICKET_STATUS_TO_LABELS["backlog"] == "status:backlog"
        assert TICKET_STATUS_TO_LABELS["todo"] == "status:todo"
        assert TICKET_STATUS_TO_LABELS["in_progress"] == "status:in_progress"
        assert TICKET_STATUS_TO_LABELS["review"] == "status:review"
        assert TICKET_STATUS_TO_LABELS["done"] == "status:done"

    def test_priority_to_labels(self):
        assert PRIORITY_TO_LABELS["low"] == "priority:low"
        assert PRIORITY_TO_LABELS["medium"] == "priority:medium"
        assert PRIORITY_TO_LABELS["high"] == "priority:high"
        assert PRIORITY_TO_LABELS["critical"] == "priority:critical"

    def test_label_to_ticket_status(self):
        assert LABEL_TO_TICKET_STATUS["status:backlog"] == "backlog"
        assert LABEL_TO_TICKET_STATUS["status:done"] == "done"

    def test_label_to_priority(self):
        assert LABEL_TO_PRIORITY["priority:low"] == "low"
        assert LABEL_TO_PRIORITY["priority:critical"] == "critical"


class TestGitHubIntegrationSync:
    def test_sync_ticket_to_issue_creates_new(self, github_integration):
        issue = github_integration.sync_ticket_to_issue("ticket-1", 1)
        assert issue.id == "ticket-1"
        assert issue.number == 1

    def test_sync_ticket_to_issue_returns_existing(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 1)
        issue = github_integration.sync_ticket_to_issue("ticket-1", 1)
        assert issue.number == 1


class TestGitHubIntegrationUpdateIssue:
    def test_update_issue_status(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 1)
        github_integration.update_issue_status(1, "in_progress")
        issue = github_integration._issues[1]
        assert "status:in_progress" in issue.labels

    def test_update_issue_status_replaces_old(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 1)
        github_integration.update_issue_status(1, "in_progress")
        github_integration.update_issue_status(1, "done")
        issue = github_integration._issues[1]
        assert "status:done" in issue.labels
        assert "status:in_progress" not in issue.labels

    def test_update_issue_status_nonexistent(self, github_integration):
        github_integration.update_issue_status(999, "done")

    def test_update_issue_priority(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 1)
        github_integration.update_issue_priority(1, "high")
        issue = github_integration._issues[1]
        assert "priority:high" in issue.labels

    def test_update_issue_priority_replaces_old(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 1)
        github_integration.update_issue_priority(1, "high")
        github_integration.update_issue_priority(1, "critical")
        issue = github_integration._issues[1]
        assert "priority:critical" in issue.labels
        assert "priority:high" not in issue.labels


class TestGitHubIntegrationSetIssueClosed:
    def test_set_issue_closed_not_merged(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 1)
        github_integration.set_issue_closed(1, merged=False)
        issue = github_integration._issues[1]
        assert issue.state == GitHubIssueState.CLOSED

    def test_set_issue_closed_merged(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 1)
        github_integration.set_issue_closed(1, merged=True)
        issue = github_integration._issues[1]
        assert issue.state == GitHubIssueState.CLOSED

    def test_set_issue_closed_nonexistent(self, github_integration):
        github_integration.set_issue_closed(999)


class TestGitHubIntegrationPR:
    def test_link_pr_to_ticket(self, github_integration):
        pr = github_integration.link_pr_to_ticket(1, 10)
        assert pr.number == 1
        assert pr.issue_number == 10
        assert pr.id == "pr:1"

    def test_mark_pr_merged(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 10)
        github_integration.link_pr_to_ticket(1, 10)
        github_integration.mark_pr_merged(1)
        pr = github_integration._pull_requests[1]
        assert pr.merged is True
        assert pr.state == "closed"

    def test_mark_pr_merged_closes_issue(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 10)
        github_integration.link_pr_to_ticket(1, 10)
        github_integration.mark_pr_merged(1)
        issue = github_integration._issues[10]
        assert issue.state == GitHubIssueState.CLOSED


class TestGitHubIntegrationGet:
    def test_get_issue_for_ticket_exists(self, github_integration):
        github_integration.sync_ticket_to_issue("ticket-1", 1)
        issue = github_integration.get_issue_for_ticket("ticket-1")
        assert issue is not None

    def test_get_issue_for_ticket_not_exists(self, github_integration):
        issue = github_integration.get_issue_for_ticket("nonexistent")
        assert issue is None

    def test_get_prs_for_issue(self, github_integration):
        github_integration.link_pr_to_ticket(1, 10)
        github_integration.link_pr_to_ticket(2, 10)
        prs = github_integration.get_prs_for_issue(10)
        assert len(prs) == 2

    def test_get_prs_for_issue_none(self, github_integration):
        prs = github_integration.get_prs_for_issue(999)
        assert prs == []