#!/usr/bin/env python3
from company.cli import create_agent, create_team, create_ticket, assign_ticket, update_ticket_status, create_meeting, attend_meeting
from company.models import Role, Level, TeamType, TicketPriority, TicketStatus, MeetingType

po = create_agent("agent-1", Role.PO, Level.L5)
dev1 = create_agent("agent-2", Role.DEVELOPER, Level.L3)
dev2 = create_agent("agent-3", Role.DEVELOPER, Level.L3)
designer = create_agent("agent-4", Role.DESIGNER, Level.L4)

eng_team = create_team("team-1", TeamType.ENGINEERING, "agent-1")
eng_team.add_member("agent-2")
eng_team.add_member("agent-3")

design_team = create_team("team-2", TeamType.DESIGN, "agent-4")

ticket1 = create_ticket("ticket-1", TicketPriority.HIGH)
ticket2 = create_ticket("ticket-2", TicketPriority.MEDIUM)
ticket3 = create_ticket("ticket-3", TicketPriority.LOW)

assign_ticket("ticket-1", "agent-2")
assign_ticket("ticket-2", "agent-3")

update_ticket_status("ticket-1", TicketStatus.IN_PROGRESS)
update_ticket_status("ticket-2", TicketStatus.REVIEW)

meeting = create_meeting("meeting-1", MeetingType.DAILY_STANDUP, "agent-1")
attend_meeting("meeting-1", "agent-1")
attend_meeting("meeting-1", "agent-2")
attend_meeting("meeting-1", "agent-3")

print("Sample data created successfully!")