from __future__ import annotations
from typing import TYPE_CHECKING, List, Any
from dataclasses import dataclass
from .task_analyzer import TaskAnalysis, TaskComplexity, TeamStructure

if TYPE_CHECKING:
    from ..models.agent import Agent
    from ..models.company import Company
    from ..models.enums import AgentRole, AgentLevel, TeamType, TicketPriority


@dataclass
class RecruitmentPlan:
    initial_roles: List[Any]
    team_structures: List[TeamStructure]
    initial_tickets: List[str]


class Recruiter:
    _role_names = {}

    def __init__(self, company: "Company"):
        self.company = company
        self._agent_counter = 0

    def recruit_initial_team(self, analysis: TaskAnalysis) -> List["Agent"]:
        from ..models.enums import AgentRole, AgentLevel, TeamType
        recruited_agents = []
        
        ceo = self._recruit_ceo()
        recruited_agents.append(ceo)

        if analysis.complexity == TaskComplexity.SMALL:
            dev = self._recruit_developer(ceo.id, AgentLevel.MID)
            recruited_agents.append(dev)
        elif analysis.complexity == TaskComplexity.MEDIUM:
            po = self._recruit_po(ceo.id)
            recruited_agents.append(po)
            
            eng_team = self._create_team("Engineering Team", TeamType.ENGINEERING, po.id)
            
            dev1 = self._recruit_developer(po.id, AgentLevel.SENIOR)
            dev2 = self._recruit_developer(po.id, AgentLevel.MID)
            qa = self._recruit_reviewer(po.id, AgentLevel.MID)
            recruited_agents.extend([dev1, dev2, qa])
            
        elif analysis.complexity == TaskComplexity.LARGE:
            po = self._recruit_po(ceo.id)
            tech_lead = self._recruit_developer(ceo.id, AgentLevel.LEAD)
            recruited_agents.extend([po, tech_lead])

            eng_team = self._create_team("Engineering Team", TeamType.ENGINEERING, tech_lead.id)
            dev1 = self._recruit_developer(tech_lead.id, AgentLevel.SENIOR)
            dev2 = self._recruit_developer(tech_lead.id, AgentLevel.SENIOR)
            dev3 = self._recruit_developer(tech_lead.id, AgentLevel.MID)
            qa = self._recruit_reviewer(tech_lead.id, AgentLevel.SENIOR)
            recruited_agents.extend([dev1, dev2, dev3, qa])

            for req in analysis.requirements:
                if req == "design":
                    design_lead = self._recruit_designer(ceo.id, AgentLevel.LEAD)
                    design_team = self._create_team("Design Team", TeamType.DESIGN, design_lead.id)
                    designer = self._recruit_designer(design_lead.id, AgentLevel.MID)
                    recruited_agents.extend([design_lead, designer])

        else:
            po = self._recruit_po(ceo.id)
            cto = self._recruit_developer(ceo.id, AgentLevel.DIRECTOR)
            recruited_agents.extend([po, cto])

            eng_team = self._create_team("Engineering", TeamType.ENGINEERING, cto.id)
            for i in range(5):
                dev = self._recruit_developer(cto.id, AgentLevel.SENIOR if i < 3 else AgentLevel.MID)
                recruited_agents.append(dev)
            
            qa_lead = self._recruit_reviewer(cto.id, AgentLevel.LEAD)
            qa = self._recruit_reviewer(qa_lead.id, AgentLevel.MID)
            recruited_agents.extend([qa_lead, qa])

            for req in analysis.requirements:
                if req == "design":
                    design_lead = self._recruit_designer(cto.id, AgentLevel.LEAD)
                    designer = self._recruit_designer(design_lead.id, AgentLevel.MID)
                    recruited_agents.extend([design_lead, designer])

        return recruited_agents

    def create_initial_tickets(self, task_description: str, agents: List["Agent"], analysis: TaskAnalysis) -> List:
        from ..models.enums import AgentRole, TicketPriority
        tickets = []
        
        main_ticket = self.company.create_ticket(
            title=f"Project: {task_description[:50]}",
            description=task_description,
            priority=TicketPriority.HIGH,
            complexity_estimate=analysis.estimated_duration_weeks
        )
        tickets.append(main_ticket)

        if analysis.complexity in [TaskComplexity.MEDIUM, TaskComplexity.LARGE, TaskComplexity.EPIC]:
            for req in analysis.requirements:
                ticket = self.company.create_ticket(
                    title=f"Implement {req} functionality",
                    description=f"Implement {req} based on task requirements",
                    priority=TicketPriority.MEDIUM,
                    complexity_estimate=2 if req in ["frontend", "backend"] else 1
                )
                tickets.append(ticket)

        po_agents = [a for a in agents if a.role == AgentRole.PO]
        if po_agents:
            for ticket in tickets:
                self.company.assign_ticket(ticket.id, po_agents[0].id)

        return tickets

    def _recruit_ceo(self) -> "Agent":
        from ..models.enums import AgentRole, AgentLevel
        self._agent_counter += 1
        return self.company.create_agent(
            name=f"CEO-{self._agent_counter:03d}",
            role=AgentRole.CLIENT,
            level=AgentLevel.C_LEVEL
        )

    def _recruit_po(self, boss_id: str) -> "Agent":
        from ..models.enums import AgentRole, AgentLevel
        self._agent_counter += 1
        return self.company.create_agent(
            name=f"Product Owner-{self._agent_counter:03d}",
            role=AgentRole.PO,
            level=AgentLevel.MANAGER,
            boss_id=boss_id
        )

    def _recruit_developer(self, boss_id: str, level: "AgentLevel") -> "Agent":
        from ..models.enums import AgentRole, AgentLevel
        self._agent_counter += 1
        return self.company.create_agent(
            name=f"Developer-{self._agent_counter:03d}",
            role=AgentRole.DEVELOPER,
            level=level,
            boss_id=boss_id
        )

    def _recruit_designer(self, boss_id: str, level: "AgentLevel") -> "Agent":
        from ..models.enums import AgentRole, AgentLevel
        self._agent_counter += 1
        return self.company.create_agent(
            name=f"Designer-{self._agent_counter:03d}",
            role=AgentRole.DESIGNER,
            level=level,
            boss_id=boss_id
        )

    def _recruit_reviewer(self, boss_id: str, level: "AgentLevel") -> "Agent":
        from ..models.enums import AgentRole, AgentLevel
        self._agent_counter += 1
        return self.company.create_agent(
            name=f"QA Engineer-{self._agent_counter:03d}",
            role=AgentRole.REVIEWER,
            level=level,
            boss_id=boss_id
        )

    def _create_team(self, name: str, team_type: "TeamType", leader_id: str):
        return self.company.create_team(
            name=name,
            team_type=team_type,
            leader_id=leader_id
        )