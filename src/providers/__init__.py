import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, model: str, **kwargs) -> str:
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        pass


def get_provider() -> LLMProvider:
    provider = os.getenv("COMPANY_LLM_PROVIDER", "openrouter").lower()
    if provider == "openrouter":
        from .openrouter import OpenRouterProvider
        return OpenRouterProvider()
    elif provider == "github_copilot":
        from .github_copilot import GitHubCopilotProvider
        return GitHubCopilotProvider()
    elif provider == "kilo_gateway":
        from .kilo_gateway import KiloGatewayProvider
        return KiloGatewayProvider()
    elif provider == "ollama":
        from .ollama import OllamaProvider
        return OllamaProvider()
    else:
        from .openrouter import OpenRouterProvider
        return OpenRouterProvider()