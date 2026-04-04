from src.models.company import Company
from src.models.enums import AgentRole, AgentLevel, TeamType, TicketStatus, TicketPriority


def main():
    company = Company()
    
    print("=== Creating Agents ===")
    po = company.create_agent("Alice", AgentRole.PO, AgentLevel.VP)
    print(f"Created PO: {po.name} (id: {po.id})")
    
    dev_lead = company.create_agent("Bob", AgentRole.DEVELOPER, AgentLevel.LEAD)
    print(f"Created Dev Lead: {dev_lead.name} (id: {dev_lead.id})")
    
    dev1 = company.create_agent("Charlie", AgentRole.DEVELOPER, AgentLevel.SENIOR)
    print(f"Created Dev1: {dev1.name} (id: {dev1.id})")
    
    designer = company.create_agent("Diana", AgentRole.DESIGNER, AgentLevel.MID)
    print(f"Created Designer: {designer.name} (id: {designer.id})")
    
    print("\n=== Creating Teams ===")
    product_team = company.create_team("Product Team", TeamType.PRODUCT, leader_id=po.id)
    print(f"Created team: {product_team.name} (id: {product_team.id})")
    
    engineering_team = company.create_team("Engineering Team", TeamType.ENGINEERING, leader_id=dev_lead.id)
    print(f"Created team: {engineering_team.name} (id: {engineering_team.id})")
    
    design_team = company.create_team("Design Team", TeamType.DESIGN, leader_id=designer.id)
    print(f"Created team: {design_team.name} (id: {design_team.id})")
    
    print("\n=== Recruiting to Team ===")
    new_dev = company.recruit_to_team(dev_lead.id, "Eve", AgentRole.DEVELOPER, AgentLevel.JUNIOR)
    if new_dev:
        print(f"Recruited: {new_dev.name} to team {engineering_team.name}")
    
    print("\n=== Forming Subteam ===")
    frontend_subteam = company.form_subteam(dev_lead.id, "Frontend Subteam", TeamType.SUBTEAM)
    if frontend_subteam:
        print(f"Created subteam: {frontend_subteam.name} (parent: {product_team.id})")
    
    print("\n=== Creating Tickets ===")
    ticket1 = company.create_ticket(
        title="Build user authentication",
        description="Implement login/logout functionality",
        team_id=engineering_team.id,
        reporter_id=po.id,
        priority=TicketPriority.HIGH,
        complexity_estimate=5
    )
    print(f"Created ticket: {ticket1.title} (id: {ticket1.id}, status: {ticket1.status.value})")
    
    ticket2 = company.create_ticket(
        title="Design new landing page",
        description="Create mockups for the new landing page",
        team_id=design_team.id,
        reporter_id=po.id,
        priority=TicketPriority.MEDIUM,
        complexity_estimate=3
    )
    print(f"Created ticket: {ticket2.title} (id: {ticket2.id}, status: {ticket2.status.value})")
    
    ticket3 = company.create_ticket(
        title="API documentation",
        description="Write comprehensive API docs",
        team_id=engineering_team.id,
        reporter_id=po.id,
        priority=TicketPriority.LOW,
        complexity_estimate=2
    )
    print(f"Created ticket: {ticket3.title} (id: {ticket3.id}, status: {ticket3.status.value})")
    
    print("\n=== Assigning and Moving Tickets ===")
    company.assign_ticket(ticket1.id, dev_lead.id)
    ticket1 = company.get_ticket(ticket1.id)
    print(f"Assigned {ticket1.title} to {dev_lead.name}")
    
    ticket1.set_status(TicketStatus.TODO)
    print(f"Moved to TODO: {ticket1.title}")
    
    ticket1.set_status(TicketStatus.IN_PROGRESS)
    print(f"Moved to IN_PROGRESS: {ticket1.title}")
    
    print("\n=== Locking Ticket During Work ===")
    locked = company.lock_ticket(ticket1.id, dev_lead.id)
    print(f"Lock result: {locked}, Locked by: {ticket1.locked_by}")
    
    print("\n=== Adding Subtasks ===")
    subtask1 = ticket1.add_subtask("Implement JWT tokens")
    print(f"Added subtask: {subtask1.title}")
    subtask2 = ticket1.add_subtask("Add password reset flow")
    print(f"Added subtask: {subtask2.title}")
    
    ticket1.complete_subtask(subtask1.id)
    print(f"Completed subtask: {subtask1.title}")
    
    completed, total = ticket1.get_subtask_progress()
    print(f"Subtask progress: {completed}/{total}")
    
    print("\n=== Creating Board with Swimlanes ===")
    board = company.create_board("Main Board")
    print(f"Created board: {board.name}")
    
    company.add_ticket_to_team_swimlane(board.id, engineering_team.id, ticket1.id)
    company.add_ticket_to_team_swimlane(board.id, design_team.id, ticket2.id)
    print(f"Added tickets to swimlanes")
    
    print("\n=== Final Ticket Statuses ===")
    for ticket in company.tickets.values():
        print(f"  {ticket.id}: {ticket.title} - {ticket.status.value} (priority: {ticket.priority.value})")
    
    print("\n=== Team Members ===")
    team = company.get_team(engineering_team.id)
    print(f"Team: {team.name}, Leader: {team.leader_id}, Members: {team.member_ids}")


if __name__ == "__main__":
    main()
