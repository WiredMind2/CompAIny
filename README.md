# CompAIny

CompAIny is an LLM-based company simulation framework implementing AGILE methodology. It simulates a complete corporate structure with agents, teams, tickets, and meetings, powered by large language models.

## Project Overview

CompAIny provides a simulated company environment where autonomous AI agents perform work following AGILE principles. The system models:

- **Agent Hierarchy**: Different roles (Engineer, Product Manager, Designer, QA) at various levels (Junior, Mid, Senior, Lead, Principal)
- **Teams**: Cross-functional teams organized with leaders and subteams
- **Tickets**: Work items with priorities, complexity estimates, and assignment tracking
- **Meetings**: Daily standups, planning sessions, retrospectives, and reviews
- **Communication Rules**: Structured messaging between agents following n+1/n/n-1 patterns

## Architecture

### Agent Hierarchy

```
Principal
  └─ Lead
       ├─ Senior
       │    ├─ Mid
       │    │   └─ Junior
       │    └─ Mid
       └─ Senior
```

### Teams

- **Feature Teams**: Deliver product features
- **Platform Teams**: Build infrastructure
- **Subteams**: Child teams under parent teams

### Communication Rules

CompAIny enforces three communication patterns:

- **n+1**: Subordinates report to their direct boss (one manager)
- **n**: Peers on the same team communicate freely
- **n-1**: Cross-team communication is restricted (only through shared managers)

### Core Models

- `Company`: Central hub managing all entities
- `Agent`: Individual contributor with role, level, and memory
- `Team`: Group of agents with a leader
- `Ticket`: Work item with status, priority, and assignee
- `Meeting`: Scheduled event with participants and reports

## Quickstart

```python
from src.models.company import Company
from src.models.enums import AgentRole, AgentLevel, TeamType

company = Company()

ceo = company.create_agent("Alice", AgentRole.PRODUCT_MANAGER, AgentLevel.PRINCIPAL)
lead = company.create_agent("Bob", AgentRole.ENGINEER, AgentLevel.LEAD, boss_id=ceo.id)

engineering = company.create_team("Engineering", TeamType.FEATURE, leader_id=lead.id)

engineer = company.recruit_to_team(
    leader_id=lead.id,
    new_agent_name="Charlie",
    role=AgentRole.ENGINEER,
    level=AgentLevel.MID
)

ticket = company.create_ticket(
    title="Implement login",
    description="Add OAuth login flow",
    team_id=engineering.id,
    priority=TicketPriority.HIGH
)

company.assign_ticket(ticket.id, engineer.id)
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

### Creating a Team Structure

```python
from src.models.company import Company
from src.models.enums import AgentRole, AgentLevel, TeamType

company = Company()

pm = company.create_agent("Product Manager", AgentRole.PRODUCT_MANAGER, AgentLevel.LEAD)
eng_lead = company.create_agent("Engineering Lead", AgentRole.ENGINEER, AgentLevel.LEAD)

product_team = company.create_team("Product", TeamType.FEATURE, leader_id=pm.id)
eng_team = company.create_team("Engineering", TeamType.FEATURE, leader_id=eng_lead.id)

senior_eng = company.recruit_to_team(eng_lead.id, "Senior Engineer", AgentRole.ENGINEER, AgentLevel.SENIOR)
```

### Managing Tickets

```python
ticket = company.create_ticket(
    title="Fix bug #123",
    description="Users cannot log in with Google",
    team_id=eng_team.id,
    priority=TicketPriority.CRITICAL
)

company.assign_ticket(ticket.id, senior_eng.id)
company.lock_ticket(ticket.id, senior_eng.id)

ticket.work()
company.unlock_ticket(ticket.id, senior_eng.id)
ticket.complete()
```

### Running Meetings

```python
from src.models.meeting import Meeting, MeetingType

standup = Meeting(
    id="meeting-1",
    type=MeetingType.STANDUP,
    team_id=eng_team.id,
    host_id=eng_lead.id
)

standup.add_participant(senior_eng.id)
standup.add_report("Working on ticket #123")
standup.complete()
```

## Installation

```bash
pip install -r requirements.txt
```

## License

MIT
