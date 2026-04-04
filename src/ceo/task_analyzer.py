from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Dict, Set
from enum import Enum

if TYPE_CHECKING:
    from ..models.enums import AgentRole, TeamType
else:
    from ..models.enums import AgentRole, TeamType


class TaskComplexity(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EPIC = "epic"


@dataclass
class Requirement:
    category: str
    keywords: Set[str]


@dataclass
class TeamStructure:
    team_type: TeamType
    roles_needed: List[AgentRole]
    size_estimate: int


@dataclass
class TaskAnalysis:
    complexity: TaskComplexity
    requirements: List[str]
    team_structure: List[TeamStructure]
    estimated_duration_weeks: int


class TaskAnalyzer:
    def __init__(self):
        self._requirement_categories = {
            "frontend": Requirement(
                category="frontend",
                keywords={"react", "vue", "angular", "ui", "frontend", "interface", "website", "web", "javascript", "typescript", "css", "component", "app"}
            ),
            "backend": Requirement(
                category="backend",
                keywords={"api", "server", "backend", "database", "rest", "graphql", "service", "endpoint", "python", "node", "java", "go"}
            ),
            "authentication": Requirement(
                category="authentication",
                keywords={"auth", "login", "authentication", "oauth", "jwt", "password", "session", "user", "register", "signup"}
            ),
            "mobile": Requirement(
                category="mobile",
                keywords={"mobile", "ios", "android", "app", "react native", "flutter", "swift", "kotlin"}
            ),
            "devops": Requirement(
                category="devops",
                keywords={"deploy", "docker", "kubernetes", "ci", "cd", "pipeline", "infrastructure", "cloud", "aws", "azure", "gcp"}
            ),
            "data": Requirement(
                category="data",
                keywords={"data", "analytics", "ml", "machine learning", "ai", "database", "sql", "nosql", "warehouse"}
            ),
            "design": Requirement(
                category="design",
                keywords={"design", "ui", "ux", "figma", "sketch", "prototype", "wireframe", "mockup", "visual"}
            ),
            "testing": Requirement(
                category="testing",
                keywords={"test", "qa", "quality", "automation", "selenium", "unittest", "jest", "cypress"}
            ),
            "product": Requirement(
                category="product",
                keywords={"product", "roadmap", "feature", "requirement", "spec", "story", "epic"}
            ),
            "security": Requirement(
                category="security",
                keywords={"security", "encryption", "ssl", "certificate", "penetration", "vulnerability"}
            ),
        }

    def analyze(self, task_description: str) -> TaskAnalysis:
        task_lower = task_description.lower()
        
        detected_requirements = self._detect_requirements(task_lower)
        complexity = self._estimate_complexity(task_lower, detected_requirements)
        team_structure = self._suggest_team_structure(detected_requirements, complexity)
        duration = self._estimate_duration(complexity, detected_requirements)
        
        return TaskAnalysis(
            complexity=complexity,
            requirements=detected_requirements,
            team_structure=team_structure,
            estimated_duration_weeks=duration
        )

    def _detect_requirements(self, task_lower: str) -> List[str]:
        detected = []
        for category, req in self._requirement_categories.items():
            if req.keywords & set(task_lower.split()):
                detected.append(category)
            else:
                for keyword in req.keywords:
                    if keyword in task_lower:
                        detected.append(category)
                        break
        return list(set(detected))

    def _estimate_complexity(self, task_lower: str, requirements: List[str]) -> TaskComplexity:
        score = 0
        
        if any(kw in task_lower for kw in ["complex", "large", "enterprise", "system", "platform"]):
            score += 3
        if any(kw in task_lower for kw in ["simple", "basic", "small", "quick"]):
            score -= 2
        
        score += len(requirements) * 1.5
        
        has_frontend = "frontend" in requirements
        has_backend = "backend" in requirements
        has_auth = "authentication" in requirements
        has_mobile = "mobile" in requirements
        has_data = "data" in requirements
        has_devops = "devops" in requirements
        
        if has_frontend and has_backend:
            score += 2
        if has_auth:
            score += 1
        if has_mobile:
            score += 2
        if has_data:
            score += 2
        if has_devops:
            score += 1

        if score >= 8:
            return TaskComplexity.EPIC
        elif score >= 5:
            return TaskComplexity.LARGE
        elif score >= 2:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.SMALL

    def _suggest_team_structure(self, requirements: List[str], complexity: TaskComplexity) -> List[TeamStructure]:
        structures = []
        
        if complexity == TaskComplexity.SMALL:
            structures.append(TeamStructure(
                team_type=TeamType.ENGINEERING,
                roles_needed=[AgentRole.DEVELOPER],
                size_estimate=1
            ))
        elif complexity == TaskComplexity.MEDIUM:
            structures.append(TeamStructure(
                team_type=TeamType.PRODUCT,
                roles_needed=[AgentRole.PO],
                size_estimate=1
            ))
            structures.append(TeamStructure(
                team_type=TeamType.ENGINEERING,
                roles_needed=[AgentRole.DEVELOPER, AgentRole.REVIEWER],
                size_estimate=2
            ))
        elif complexity == TaskComplexity.LARGE:
            structures.append(TeamStructure(
                team_type=TeamType.PRODUCT,
                roles_needed=[AgentRole.PO],
                size_estimate=1
            ))
            structures.append(TeamStructure(
                team_type=TeamType.ENGINEERING,
                roles_needed=[AgentRole.DEVELOPER, AgentRole.REVIEWER],
                size_estimate=3
            ))
            if "design" in requirements:
                structures.append(TeamStructure(
                    team_type=TeamType.DESIGN,
                    roles_needed=[AgentRole.DESIGNER],
                    size_estimate=1
                ))
        else:
            structures.append(TeamStructure(
                team_type=TeamType.EXECUTIVE,
                roles_needed=[],
                size_estimate=0
            ))
            structures.append(TeamStructure(
                team_type=TeamType.PRODUCT,
                roles_needed=[AgentRole.PO],
                size_estimate=1
            ))
            structures.append(TeamStructure(
                team_type=TeamType.ENGINEERING,
                roles_needed=[AgentRole.DEVELOPER, AgentRole.REVIEWER],
                size_estimate=5
            ))
            if "design" in requirements:
                structures.append(TeamStructure(
                    team_type=TeamType.DESIGN,
                    roles_needed=[AgentRole.DESIGNER],
                    size_estimate=2
                ))
            if "testing" in requirements:
                structures.append(TeamStructure(
                    team_type=TeamType.ENGINEERING,
                    roles_needed=[AgentRole.REVIEWER],
                    size_estimate=1
                ))

        return structures

    def _estimate_duration(self, complexity: TaskComplexity, requirements: List[str]) -> int:
        base_duration = {
            TaskComplexity.SMALL: 1,
            TaskComplexity.MEDIUM: 4,
            TaskComplexity.LARGE: 12,
            TaskComplexity.EPIC: 26
        }[complexity]
        
        extra = len(requirements) * 0.5
        return max(1, int(base_duration + extra))