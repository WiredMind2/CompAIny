import os
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def complete(self, prompt: str, model: str, **kwargs) -> str:
        """Generate a completion for the given prompt."""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        """Generate a chat completion for the given messages."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass


def get_provider(provider_type: Optional[str] = None) -> LLMProvider:
    """Factory function to get an LLM provider instance."""
    if provider_type is None:
        provider_type = os.environ.get("COMPANY_LLM_PROVIDER", "openrouter")
    
    provider_type = provider_type.lower()
    
    if provider_type == "openrouter":
        from .openrouter import OpenRouterProvider
        return OpenRouterProvider()
    elif provider_type == "github_copilot":
        from .github_copilot import GitHubCopilotProvider
        return GitHubCopilotProvider()
    elif provider_type == "kilo_gateway":
        from .kilo_gateway import KiloGatewayProvider
        return KiloGatewayProvider()
    elif provider_type == "ollama":
        from .ollama import OllamaProvider
        return OllamaProvider()
    else:
        from .openrouter import OpenRouterProvider
        return OpenRouterProvider()


__all__ = ["LLMProvider", "get_provider"]