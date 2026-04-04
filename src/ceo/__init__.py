from __future__ import annotations
from typing import TYPE_CHECKING, List
from .task_analyzer import TaskAnalyzer, TaskAnalysis
from .recruiter import Recruiter

if TYPE_CHECKING:
    from ..models.company import Company
    from ..models.agent import Agent


class CEOAgent:
    def __init__(self, company: "Company"):
        self.company = company
        self.task_analyzer = TaskAnalyzer()
        self.recruiter = Recruiter(company)

    def bootstrap(self, task_description: str) -> "Company":
        analysis = self.task_analyzer.analyze(task_description)
        
        agents = self.recruiter.recruit_initial_team(analysis)
        
        tickets = self.recruiter.create_initial_tickets(task_description, agents, analysis)
        
        return self.company

    def analyze_task(self, task_description: str) -> TaskAnalysis:
        return self.task_analyzer.analyze(task_description)

    def get_team_composition(self, analysis: TaskAnalysis) -> dict:
        composition = {
            "complexity": analysis.complexity.value,
            "estimated_weeks": analysis.estimated_duration_weeks,
            "requirements": analysis.requirements,
            "teams": []
        }
        
        for structure in analysis.team_structure:
            composition["teams"].append({
                "type": structure.team_type.value,
                "size": structure.size_estimate,
                "roles": [r.value for r in structure.roles_needed]
            })
        
        return composition