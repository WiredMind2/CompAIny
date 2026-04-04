# CompAIny

An AI-driven company management system that implements autonomous software engineering teams using AGILE methodologies.

## Overview

CompAIny is a system for managing autonomous AI agents organized into hierarchical teams that can plan, execute, and deliver software projects. The system handles ticket management, meeting ceremonies, agent memory/persistence, and integrates with GitHub.

## Architecture

### Core Data Models

#### Agent
- `id`: Unique identifier (UUID)
- `role`: PO (Product Owner), Developer, Designer, Reviewer, HR
- `level`: 1-10 (hierarchy level)
- `team_id`: Reference to team
- `memory`: Short-term context + long-term patterns

#### Team
- `id`: Unique identifier
- `type`: Engineering, Design, Product, etc.
- `leader`: Team lead agent
- `members`: List of agent IDs

#### Ticket
- `status`: backlog / todo / in_progress / review / done
- `priority`: low / medium / high / critical
- `assignee`: Agent ID
- `github_issue_id`: Optional GitHub issue link
- `complexity`: Estimated complexity score

#### Meeting
- `type`: daily_standup / sprint_planning / retrospective
- `participants`: List of agent IDs
- `reports`: Meeting outputs

### Hierarchy Levels

Agents operate in a strict hierarchy (levels 1-10):
- Level 10: CEO/Principal
- Level 9: Directors
- Level 8: Senior Managers
- ...
- Level 1: Junior agents

## AGILE Process

### Meeting Types

#### Daily Standup
- Purpose: Progress reports
- Participants: Team members
- Output: Status updates propagated up hierarchy

#### Sprint Planning
- Purpose: Subtask breakdown, complexity estimation
- Activities:
  - Recruitment decisions (leader can recruit for large tasks)
  - Ticket acceptance/rejection
  - Subteam formation for complex work
- Output: Sprint backlog

#### Retrospective
- Purpose: Process improvement
- Output: Action items for next sprint

### Kanban Workflow

```
backlog → todo → in_progress → review → done
```

- Tickets locked during `in_progress` to prevent duplicate work
- Swimlanes per team for visual organization

## Communication Rules

Strict communication hierarchy enforced:
- Agents can only message:
  - **Boss** (level n+1): Reports, escalations
  - **Peers** (level n): Collaborations
  - **Underlings** (level n-1): Task assignments

## GitHub Integration

- Sync tickets with GitHub issues
- Map status to labels
- Link PRs to completed tickets

## Human Agents

- Humans can register as agents with any role
- Indistinguishable to AI agents
- Can attend meetings and receive tasks
- Support for Client role

## Quickstart

```python
from company import Company

# Initialize company
company = Company("Acme AI")

# Create agents
po = company.create_agent(role="PO", level=5)
dev = company.create_agent(role="Developer", level=3)

# Create team
team = company.create_team(name="Backend", leader=po)
team.recruit(dev)

# Create ticket
ticket = team.create_ticket(
    title="Build API",
    description="REST API for users",
    priority="high"
)

# Assign and work
ticket.assign(dev)
dev.work_on(ticket)

# Run daily standup
meeting = team.schedule_meeting("daily_standup")
meeting.run()
```

## CLI Commands

```bash
# View teams
company-cli teams list

# View tickets
company-cli tickets list --team backend

# Attend meetings
company-cli meeting attend <meeting_id>

# Assign tasks
company-cli ticket assign <ticket_id> <agent_id>

# Check progress
company-cli progress
```

## REST API

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /teams | List all teams |
| GET | /teams/:id | Get team details |
| GET | /tickets | List tickets |
| POST | /tickets | Create ticket |
| PUT | /tickets/:id | Update ticket |
| GET | /agents | List agents |
| POST | /meetings | Schedule meeting |
| GET | /meetings/:id | Get meeting details |

### Response Format

All responses in JSON:
```json
{
  "status": "success",
  "data": { ... }
}
```

## Agent Memory

- **Short-term**: Current task state, active tickets
- **Long-term**: Past projects, learned patterns
- **Persistence**: SQLite database for agent state

## License

MIT
