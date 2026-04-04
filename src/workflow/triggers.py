from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any, Optional
from enum import Enum


class WorkflowEvent(str, Enum):
    TICKET_COMPLETED = "ticket_completed"
    TICKET_BLOCKED = "ticket_blocked"
    TICKET_REVIEW_COMPLETED = "ticket_review_completed"
    TICKET_ACCEPTED = "ticket_accepted"
    TEAM_COMPLETED = "team_completed"
    MEETING_REQUESTED = "meeting_requested"


@dataclass
class WorkflowEventData:
    event: WorkflowEvent
    agent_id: str
    team_id: Optional[str] = None
    ticket_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventTrigger:
    def __init__(self, event: WorkflowEvent, handler: Callable[[WorkflowEventData], None]):
        self.event = event
        self.handler = handler

    def trigger(self, data: WorkflowEventData) -> None:
        if data.event == self.event:
            self.handler(data)


class EventBus:
    def __init__(self):
        self._subscribers: Dict[WorkflowEvent, List[EventTrigger]] = {}

    def subscribe(self, event: WorkflowEvent, handler: Callable[[WorkflowEventData], None]) -> EventTrigger:
        if event not in self._subscribers:
            self._subscribers[event] = []
        trigger = EventTrigger(event, handler)
        self._subscribers[event].append(trigger)
        return trigger

    def unsubscribe(self, trigger: EventTrigger) -> None:
        if trigger.event in self._subscribers:
            if trigger in self._subscribers[trigger.event]:
                self._subscribers[trigger.event].remove(trigger)

    def emit(self, data: WorkflowEventData) -> None:
        if data.event in self._subscribers:
            for trigger in self._subscribers[data.event]:
                trigger.trigger(data)

    def get_subscribers(self, event: WorkflowEvent) -> List[EventTrigger]:
        return self._subscribers.get(event, [])