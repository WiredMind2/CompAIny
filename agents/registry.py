from typing import Dict, Optional, List
from . import Agent, AgentRole, AgentType


class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        self.agents[agent.id] = agent

    def get(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def list_agents(self, team_id: Optional[str] = None, role: Optional[AgentRole] = None) -> List[Agent]:
        result = list(self.agents.values())
        if team_id:
            result = [a for a in result if a.team_id == team_id]
        if role:
            result = [a for a in result if a.role == role]
        return result

    def list_humans(self) -> List[Agent]:
        return [a for a in self.agents.values() if a.agent_type == AgentType.HUMAN]

    def list_ai_agents(self) -> List[Agent]:
        return [a for a in self.agents.values() if a.agent_type == AgentType.AI]

    def remove(self, agent_id: str) -> bool:
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    def register_human(
        self,
        id: str,
        name: str,
        role: AgentRole = AgentRole.CLIENT,
        team_id: Optional[str] = None,
    ) -> Agent:
        human = Agent(
            id=id,
            name=name,
            role=role,
            level=1,
            team_id=team_id,
            boss_id=None,
            agent_type=AgentType.HUMAN,
        )
        self.register(human)
        return human