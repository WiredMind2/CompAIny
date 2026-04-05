# CompAIny

CompAIny is an LLM-based company simulation framework implementing AGILE methodology. It simulates a complete corporate structure with agents, teams, tickets, and meetings, powered by large language models.

## Project Overview

CompAIny provides a simulated company environment where autonomous AI agents perform work following AGILE principles. The system models:

- **Agent Hierarchy**: Different roles (Engineer, Product Manager, Designer, QA) at various levels (Junior, Mid, Senior, Lead, Principal)
- **Teams**: Cross-functional teams organized with leaders and subteams
- **Tickets**: Work items with priorities, complexity estimates, and assignment tracking
- **Meetings**: Daily standups, planning sessions, retrospectives, and reviews
- **Communication Rules**: Structured messaging between agents following n+1/n/n-1 patterns

## Quickstart

```python
from src.models.company import Company
from src.models.enums import AgentRole, AgentLevel, TeamType, TicketPriority

# Create a company
company = Company()

# Create agents with hierarchy
ceo = company.create_agent("Alice", AgentRole.PRODUCT_MANAGER, AgentLevel.MANAGER)
lead = company.create_agent("Bob", AgentRole.DEVELOPER, AgentLevel.LEAD, boss_id=ceo.id)

# Create a team
engineering = company.create_team("Engineering", TeamType.ENGINEERING, leader_id=lead.id)

# Recruit an agent to the team
engineer = company.recruit_to_team(
    leader_id=lead.id,
    new_agent_name="Charlie",
    role=AgentRole.DEVELOPER,
    level=AgentLevel.MID
)

# Create and assign a ticket
ticket = company.create_ticket(
    title="Implement login",
    description="Add OAuth login flow",
    team_id=engineering.id,
    priority=TicketPriority.HIGH
)

company.assign_ticket(ticket.id, engineer.id)
```

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Company                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────────┐   │
│  │ Agents  │  │ Teams   │  │ Tickets │  │ Meetings      │   │
│  └─────────┘  └─────────┘  └─────────┘  └───────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │              │            │              │
         ▼              ▼            ▼              ▼
┌─────────────┐  ┌──────────┐ ┌─────────┐  ┌─────────────┐
│ CEOAgent    │  │ Team     │ │ Ticket  │  │ Meeting     │
│ (bootstrap)│  │ Leader   │ │ Board   │  │ Scheduler   │
└─────────────┘  └──────────┘ └─────────┘  └─────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Workflow Engine │
              │ (triggers/auto) │
              └─────────────────┘
```

### Agent Hierarchy

```
FOUNDER (Level 10)
    └─ C_LEVEL (Level 9)
         └─ VP (Level 8)
              └─ DIRECTOR (Level 7)
                   └─ MANAGER (Level 6)
                        └─ LEAD (Level 5)
                             ├─ SENIOR (Level 4)
                             │    ├─ MID (Level 3)
                             │    │   └─ JUNIOR (Level 2)
                             │    └─ MID (Level 3)
                             └─ SENIOR (Level 4)
```

### Data Models

| Model | Description | Key Attributes |
|-------|-------------|----------------|
| `Company` | Central hub managing all entities | agents, teams, tickets, meetings |
| `Agent` | Individual contributor with role and level | id, name, role, level, boss_id, team_id |
| `Team` | Group of agents with a leader | id, name, type, leader_id, member_ids |
| `Ticket` | Work item with status and priority | id, title, status, priority, assignee_id |
| `Meeting` | Scheduled event with participants | id, type, host_id, participant_ids |

## AGILE Process

### Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   BACKLOG   │───▶│    TODO     │───▶│IN_PROGRESS  │───▶│    DONE     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   REVIEW    │
                                        └─────────────┘
```

### Ticket Lifecycle

```python
# Create ticket in backlog
ticket = company.create_ticket(
    title="Feature request",
    description="Add dark mode",
    priority=TicketPriority.MEDIUM
)

# Move to TODO
ticket.set_status(TicketStatus.TODO)

# Assign to agent
company.assign_ticket(ticket.id, agent.id)

# Lock ticket (work begins)
company.lock_ticket(ticket.id, agent.id)

# Set to in progress
ticket.set_status(TicketStatus.IN_PROGRESS)

# Complete work
company.unlock_ticket(ticket.id, agent.id)
ticket.set_status(TicketStatus.REVIEW)

# Mark as done
company.complete_ticket(agent.id, ticket.id)
```

### Meeting Types

| Type | Purpose | Frequency |
|------|---------|-----------|
| `STANDUP` | Daily progress sync | Daily |
| `PLANNING` | Sprint planning | Weekly |
| `RETROSPECTIVE` | Process improvement | Weekly |
| `REVIEW` | Demo completed work | Weekly |

```python
from src.models.meeting import Meeting, MeetingType

# Create a daily standup
standup = company.create_meeting(
    meeting_type=MeetingType.STANDUP,
    team_id=engineering_team.id,
    host_id=lead.id
)

# Add status report
standup.add_report("Completed login feature")

# Complete meeting
standup.complete()
```

### Sprint Workflow

```python
# Pick next available ticket
ticket = company.pick_next_ticket(agent_id)

# Report blocker if stuck
company.report_blocker(agent_id, ticket.id, "Need API credentials")

# Check team completion
if company.check_team_completion(team_id):
    company.trigger_team_completion(team_id, sprint_ended=True)
```

## Communication Rules

CompAIny enforces a hierarchical communication pattern:

```
        Manager (n)
           │
    ┌──────┴──────┐
    │             │
  Peer (n)    Peer (n)
    │             │
    ▼             ▼
Subordinate    Subordinate
 (n+1)          (n+1)
```

### n+1 Rule

Subordinates report to their direct manager only. Each agent has one boss.

```python
# Agent can message their boss
agent.can_message(boss)  # True

# Agent can message their subordinates
boss.can_message(agent)  # True
```

### n Rule

Peers on the same team communicate freely.

```python
# Same team peers can communicate
peer1.can_message(peer2)  # True (same team)
```

### n-1 Rule

Cross-team communication is restricted to shared managers.

```python
# Different teams cannot communicate directly
member1.can_message(member2)  # False (different teams)
```

## API Reference

### Company

```python
company = Company()

# Bootstrap from task description
company = Company.bootstrap("Build a web application")

# Agent management
agent = company.create_agent(name, role, level, team_id=None, boss_id=None)
agent = company.get_agent(agent_id)
agent = company.recruit_to_team(leader_id, name, role, level)

# Team management
team = company.create_team(name, type, leader_id, parent_team_id=None)
team = company.get_team(team_id)
subteam = company.form_subteam(leader_id, name, type)

# Ticket management
ticket = company.create_ticket(title, description, team_id, reporter_id, priority, complexity_estimate)
ticket = company.get_ticket(ticket_id)
company.assign_ticket(ticket_id, agent_id)
company.lock_ticket(ticket_id, agent_id)
company.unlock_ticket(ticket_id, agent_id)
company.transfer_ticket(ticket_id, to_agent_id)
company.reassign_ticket_to_team(ticket_id, team_id)
ticket = company.pick_next_ticket(agent_id)
company.complete_ticket(agent_id, ticket_id)
company.report_blocker(agent_id, ticket_id, reason)

# Query methods
team_tickets = company.get_team_tickets(team_id)
tickets = company.get_tickets_by_status(status)
tickets = company.get_tickets_by_assignee(agent_id)
tickets = company.get_locked_tickets()

# Board management
board = company.create_board(name, team_id)
company.add_ticket_to_team_swimlane(board_id, team_id, ticket_id)

# Meeting management
meeting = company.create_meeting(type, team_id, host_id)
meeting = company.get_meeting(meeting_id)

# Workflow engine
company.start_workflow_engine()
company.stop_workflow_engine()
company.check_team_completion(team_id)
company.trigger_team_completion(team_id, sprint_ended=False)
```

### Agent

```python
agent.can_message(target_agent)  # Check communication permission
agent.get_role_level()            # Get level as int
agent.set_workspace(repo_url, branch, workspace_path)
agent.execute_tool(tool, **kwargs)
agent.store_tool_result(tool_call_id, result)
```

### Ticket

```python
ticket.lock(agent_id)                      # Lock for work
ticket.unlock(agent_id)                    # Unlock
ticket.assign(agent_id)                    # Assign to agent
ticket.set_status(status)                  # Set ticket status
ticket.set_priority(priority)              # Set priority
subtask = ticket.add_subtask(title)         # Add subtask
ticket.complete_subtask(subtask_id)         # Complete subtask
progress = ticket.get_subtask_progress()   # Get (completed, total)
ticket.is_locked()                          # Check if locked
```

### Team

```python
team.add_member(agent_id)
team.remove_member(agent_id)
team.add_subteam(subteam_id)
team.remove_subteam(subteam_id)
team.is_leader(agent_id)                   # Check if agent is leader
members = team.get_all_member_ids()
team.check_completion(tickets)             # Check all tickets done
```

### Meeting

```python
meeting.add_participant(agent_id)
meeting.remove_participant(agent_id)
meeting.add_report(report_text)
meeting.complete()
```

### Enums

```python
# Agent Roles
AgentRole.PO          # Product Owner
AgentRole.DEVELOPER   # Developer
AgentRole.DESIGNER    # Designer
AgentRole.REVIEWER    # Reviewer
AgentRole.HR          # HR
AgentRole.CLIENT      # Client

# Agent Levels (1-10)
AgentLevel.JUNIOR     # Level 1
AgentLevel.MID        # Level 2
AgentLevel.SENIOR     # Level 3
AgentLevel.LEAD       # Level 4
AgentLevel.MANAGER    # Level 5
AgentLevel.DIRECTOR   # Level 6
AgentLevel.VP         # Level 7
AgentLevel.C_LEVEL    # Level 8
AgentLevel.FOUNDER    # Level 9
AgentLevel.BOARD      # Level 10

# Ticket Status
TicketStatus.BACKLOG
TicketStatus.TODO
TicketStatus.IN_PROGRESS
TicketStatus.REVIEW
TicketStatus.DONE

# Ticket Priority
TicketPriority.LOW
TicketPriority.MEDIUM
TicketPriority.HIGH
TicketPriority.CRITICAL

# Team Type
TeamType.ENGINEERING
TeamType.DESIGN
TeamType.PRODUCT
TeamType.OPERATIONS
TeamType.EXECUTIVE
TeamType.SUBTEAM

# Meeting Type
MeetingType.STANDUP
MeetingType.PLANNING
MeetingType.RETROSPECTIVE
MeetingType.REVIEW
```

## LLM Providers

CompAIny supports multiple LLM providers. Set the provider via the `COMPANY_LLM_PROVIDER` environment variable:

| Provider | Env Value | Description |
|----------|-----------|-------------|
| OpenRouter | `openrouter` | Access 100+ LLMs via openrouter.ai |
| GitHub Copilot | `github_copilot` | GitHub Copilot's chat API |
| Kilo Gateway | `kilo_gateway` | Kilo's AI gateway |
| Ollama | `ollama` | Local models via Ollama |

### Environment Variables

**OpenRouter**:
```bash
COMPANY_LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-api-key
```

**GitHub Copilot**:
```bash
COMPANY_LLM_PROVIDER=github_copilot
GITHUB_COPILOT_TOKEN=your-github-token
```

**Kilo Gateway**:
```bash
COMPANY_LLM_PROVIDER=kilo_gateway
KILO_GATEWAY_API_KEY=your-api-key
```

**Ollama**:
```bash
COMPANY_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### Using the Provider

```python
from src.providers import get_provider

provider = get_provider()

# Simple completion
response = provider.complete("Hello, world!", model="openai/gpt-4o")

# Chat with messages
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"}
]
response = provider.chat(messages, model="openai/gpt-4o")
```

## Usage Examples

### Creating a Complete Team Structure

```python
from src.models.company import Company
from src.models.enums import AgentRole, AgentLevel, TeamType, TicketPriority

company = Company()

# Create leadership
ceo = company.create_agent("CEO", AgentRole.PRODUCT_MANAGER, AgentLevel.C_LEVEL)
vp_eng = company.create_agent("VP Engineering", AgentRole.DEVELOPER, AgentLevel.VP, boss_id=ceo.id)
vp_product = company.create_agent("VP Product", AgentRole.PO, AgentLevel.VP, boss_id=ceo.id)

# Create teams
eng_team = company.create_team("Engineering", TeamType.ENGINEERING, leader_id=vp_eng.id)
product_team = company.create_team("Product", TeamType.PRODUCT, leader_id=vp_product.id)

# Recruit team members
senior_eng = company.recruit_to_team(vp_eng.id, "Senior Engineer", AgentRole.DEVELOPER, AgentLevel.SENIOR)
mid_eng = company.recruit_to_team(vp_eng.id, "Mid Engineer", AgentRole.DEVELOPER, AgentLevel.MID)
designer = company.recruit_to_team(vp_product.id, "Designer", AgentRole.DESIGNER, AgentLevel.SENIOR)

# Create backlog
for i in range(10):
    ticket = company.create_ticket(
        title=f"Feature {i}",
        description=f"Implement feature {i}",
        team_id=eng_team.id,
        priority=TicketPriority.MEDIUM
    )

# Assign work
tickets = list(company.tickets.values())
company.assign_ticket(tickets[0].id, senior_eng.id)
company.assign_ticket(tickets[1].id, mid_eng.id)
```

### Running a Sprint Cycle

```python
# Start workflow engine for automation
company.start_workflow_engine()

# Daily standup
standup = company.create_meeting(MeetingType.STANDUP, eng_team.id, vp_eng.id)
standup.add_report(f"{senior_eng.name}: Working on {tickets[0].title}")
standup.add_report(f"{mid_eng.name}: Pick up {tickets[1].title}")
standup.complete()

# Agent picks up next ticket
ticket = company.pick_next_ticket(mid_eng.id)

# Complete work
company.complete_ticket(senior_eng.id, tickets[0].id)

# Sprint end - retrospective
retro = company.create_meeting(MeetingType.RETROSPECTIVE, eng_team.id, vp_eng.id)
retro.add_report("Good: Clear requirements")
retro.add_report("Improve: More pair programming")
retro.complete()

# Stop workflow
company.stop_workflow_engine()
```

### Using Subteams

```python
# Create subteam under main team
frontend_subteam = company.form_subteam(
    leader_id=senior_eng.id,
    subteam_name="Frontend",
    subteam_type=TeamType.SUBTEAM
)

# Add member to subteam
frontend_dev = company.create_agent(
    name="Frontend Dev",
    role=AgentRole.DEVELOPER,
    level=AgentLevel.MID,
    team_id=frontend_subteam.id,
    boss_id=senior_eng.id
)
```

### Managing Tickets with Subtasks

```python
ticket = company.create_ticket("Build API", "Create REST API", eng_team.id, priority=TicketPriority.HIGH)

# Add subtasks
ticket.add_subtask("Design endpoints")
ticket.add_subtask("Implement database layer")
ticket.add_subtask("Add validation")
ticket.add_subtask("Write tests")

# Complete subtasks
ticket.complete_subtask("ticket-1-subtask-1")
ticket.complete_subtask("ticket-1-subtask-2")

# Check progress
completed, total = ticket.get_subtask_progress()  # (2, 4)
```

## Installation

```bash
pip install -r requirements.txt
```

## License

MIT