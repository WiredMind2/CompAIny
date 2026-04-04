from enum import Enum
from typing import Optional, List
from datetime import datetime


class AgentRole(str, Enum):
    PO = "PO"
    DEVELOPER = "DEVELOPER"
    DESIGNER = "DESIGNER"
    REVIEWER = "REVIEWER"
    HR = "HR"
    CLIENT = "CLIENT"


class AgentLevel(int, Enum):
    JUNIOR = 1
    MID = 2
    SENIOR = 3
    LEAD = 4
    MANAGER = 5
    DIRECTOR = 6
    VP = 7
    C_LEVEL = 8
    FOUNDER = 9
    BOARD = 10


class TicketStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TeamType(str, Enum):
    ENGINEERING = "engineering"
    DESIGN = "design"
    PRODUCT = "product"
    OPERATIONS = "operations"
    EXECUTIVE = "executive"
    SUBTEAM = "subteam"