from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass, field

from .triggers import WorkflowEvent, WorkflowEventData, EventBus
from .automation import AutomationRules


@dataclass
class WorkflowEngine:
    company: Any = None
    event_bus: EventBus = field(default_factory=EventBus)
    rules: Optional[AutomationRules] = None
    _running: bool = False
    _notifications: List[Dict[str, str]] = field(default_factory=list)

    def initialize(self, company: Any) -> None:
        self.company = company
        self.rules = AutomationRules(company, self)
        self._setup_event_handlers()
        self._running = False

    def _setup_event_handlers(self) -> None:
        self.event_bus.subscribe(
            WorkflowEvent.TICKET_COMPLETED,
            self._handle_ticket_completed
        )
        self.event_bus.subscribe(
            WorkflowEvent.TEAM_COMPLETED,
            self._handle_team_completed
        )
        self.event_bus.subscribe(
            WorkflowEvent.TICKET_BLOCKED,
            self._handle_ticket_blocked
        )
        self.event_bus.subscribe(
            WorkflowEvent.TICKET_REVIEW_COMPLETED,
            self._handle_review_completed
        )
        self.event_bus.subscribe(
            WorkflowEvent.TICKET_ACCEPTED,
            self._handle_ticket_accepted
        )

    def _handle_ticket_completed(self, data: WorkflowEventData) -> None:
        if self.rules:
            self.rules.on_ticket_completed(data.agent_id, data.ticket_id, data.team_id)

    def _handle_team_completed(self, data: WorkflowEventData) -> None:
        if self.rules:
            sprint_ended = data.metadata.get("sprint_ended", False) if data.metadata else False
            self.rules.on_team_completed(data.team_id, sprint_ended)

    def _handle_ticket_blocked(self, data: WorkflowEventData) -> None:
        if self.rules:
            reason = data.metadata.get("reason", "Unknown blocker") if data.metadata else "Unknown blocker"
            self.rules.on_ticket_blocked(data.ticket_id, data.team_id, reason)

    def _handle_review_completed(self, data: WorkflowEventData) -> None:
        if self.rules:
            self.rules.on_review_completed(data.ticket_id, data.team_id)

    def _handle_ticket_accepted(self, data: WorkflowEventData) -> None:
        if self.rules:
            self.rules.on_ticket_accepted(data.ticket_id, data.team_id)

    def emit_event(self, event: WorkflowEvent, agent_id: str, team_id: Optional[str] = None,
                   ticket_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        data = WorkflowEventData(
            event=event,
            agent_id=agent_id,
            team_id=team_id,
            ticket_id=ticket_id,
            metadata=metadata or {}
        )
        self.event_bus.emit(data)

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def notify_team_lead(self, lead_agent_id: str, message: str) -> None:
        self._notifications.append({
            "agent_id": lead_agent_id,
            "message": message
        })

    def get_notifications(self) -> List[Dict[str, str]]:
        return self._notifications.copy()

    def clear_notifications(self) -> None:
        self._notifications.clear()


__all__ = ["WorkflowEngine", "WorkflowEvent", "WorkflowEventData", "EventBus"]