import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import json

from src.providers import LLMProvider, get_provider
from src.providers.openrouter import OpenRouterProvider
from src.providers.github_copilot import GitHubCopilotProvider
from src.providers.kilo_gateway import KiloGatewayProvider
from src.providers.ollama import OllamaProvider
from src.models.company import Company
from src.models.agent import Agent
from src.models.enums import AgentRole, AgentLevel


class TestLLMProviderBase:
    def test_llm_provider_is_abstract(self):
        with pytest.raises(TypeError):
            LLMProvider()


class TestGetProvider:
    def test_get_provider_default(self, monkeypatch):
        monkeypatch.delenv("COMPANY_LLM_PROVIDER", raising=False)
        provider = get_provider()
        assert isinstance(provider, OpenRouterProvider)

    def test_get_provider_openrouter(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "openrouter")
        provider = get_provider()
        assert isinstance(provider, OpenRouterProvider)

    def test_get_provider_github_copilot(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "github_copilot")
        provider = get_provider()
        assert isinstance(provider, GitHubCopilotProvider)

    def test_get_provider_kilo_gateway(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "kilo_gateway")
        provider = get_provider()
        assert isinstance(provider, KiloGatewayProvider)

    def test_get_provider_ollama(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "ollama")
        provider = get_provider()
        assert isinstance(provider, OllamaProvider)


class TestOpenRouterProvider:
    def test_openrouter_provider_init(self, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
        provider = OpenRouterProvider()
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://openrouter.ai/api/v1/chat/completions"

    def test_openrouter_complete_converts_to_chat(self, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
        provider = OpenRouterProvider()
        
        with patch.object(provider, 'chat', return_value="test response") as mock_chat:
            result = provider.complete("test prompt", model="gpt-4")
            mock_chat.assert_called_once_with(
                [{"role": "user", "content": "test prompt"}], 
                "gpt-4"
            )
            assert result == "test response"

    def test_openrouter_chat_makes_request(self, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
        provider = OpenRouterProvider()
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "test response"}}]
        }).encode()
        
        with patch('urllib.request.urlopen', return_value=mock_response):
            messages = [{"role": "user", "content": "test prompt"}]
            result = provider.chat(messages, "gpt-4")
            assert result == "test response"


class TestGitHubCopilotProvider:
    def test_github_copilot_provider_init(self, monkeypatch):
        monkeypatch.setenv("GITHUB_COPILOT_TOKEN", "test-token")
        provider = GitHubCopilotProvider()
        assert provider.api_key == "test-token"
        assert provider.base_url == "https://api.github.com/copilot/chat/completions"

    def test_github_copilot_complete_converts_to_chat(self, monkeypatch):
        monkeypatch.setenv("GITHUB_COPILOT_TOKEN", "test-token")
        provider = GitHubCopilotProvider()
        
        with patch.object(provider, 'chat', return_value="test response") as mock_chat:
            result = provider.complete("test prompt", model="gpt-4o")
            mock_chat.assert_called_once_with(
                [{"role": "user", "content": "test prompt"}], 
                "gpt-4o"
            )
            assert result == "test response"

    def test_github_copilot_chat_makes_request(self, monkeypatch):
        monkeypatch.setenv("GITHUB_COPILOT_TOKEN", "test-token")
        provider = GitHubCopilotProvider()
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "test response"}}]
        }).encode()
        
        with patch('urllib.request.urlopen', return_value=mock_response):
            messages = [{"role": "user", "content": "test prompt"}]
            result = provider.chat(messages, "gpt-4o")
            assert result == "test response"


class TestKiloGatewayProvider:
    def test_kilo_gateway_provider_init(self, monkeypatch):
        monkeypatch.setenv("KILO_GATEWAY_API_KEY", "test-key")
        monkeypatch.setenv("KILO_GATEWAY_URL", "https://custom.gateway.ai/v1")
        provider = KiloGatewayProvider()
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://custom.gateway.ai/v1"

    def test_kilo_gateway_provider_default_url(self, monkeypatch):
        monkeypatch.setenv("KILO_GATEWAY_API_KEY", "test-key")
        monkeypatch.delenv("KILO_GATEWAY_URL", raising=False)
        provider = KiloGatewayProvider()
        assert provider.base_url == "https://gateway.kilo.ai/v1/chat/completions"

    def test_kilo_gateway_complete_converts_to_chat(self, monkeypatch):
        monkeypatch.setenv("KILO_GATEWAY_API_KEY", "test-key")
        provider = KiloGatewayProvider()
        
        with patch.object(provider, 'chat', return_value="test response") as mock_chat:
            result = provider.complete("test prompt", model="claude-3-5-sonnet")
            mock_chat.assert_called_once_with(
                [{"role": "user", "content": "test prompt"}], 
                "claude-3-5-sonnet"
            )
            assert result == "test response"

    def test_kilo_gateway_chat_makes_request(self, monkeypatch):
        monkeypatch.setenv("KILO_GATEWAY_API_KEY", "test-key")
        provider = KiloGatewayProvider()
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "test response"}}]
        }).encode()
        
        with patch('urllib.request.urlopen', return_value=mock_response):
            messages = [{"role": "user", "content": "test prompt"}]
            result = provider.chat(messages, "claude-3-5-sonnet")
            assert result == "test response"


class TestOllamaProvider:
    def test_ollama_provider_init_default_url(self, monkeypatch):
        monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
        provider = OllamaProvider()
        assert provider.base_url == "http://localhost:11434"

    def test_ollama_provider_init_custom_url(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:11434")
        provider = OllamaProvider()
        assert provider.base_url == "http://custom:11434"

    def test_ollama_complete_converts_to_chat(self):
        provider = OllamaProvider()
        
        with patch.object(provider, 'chat', return_value="test response") as mock_chat:
            result = provider.complete("test prompt", model="llama2")
            mock_chat.assert_called_once_with(
                [{"role": "user", "content": "test prompt"}], 
                "llama2"
            )
            assert result == "test response"

    def test_ollama_chat_makes_request(self):
        provider = OllamaProvider()
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "message": {"content": "test response"}
        }).encode()
        
        with patch('urllib.request.urlopen', return_value=mock_response):
            messages = [{"role": "user", "content": "test prompt"}]
            result = provider.chat(messages, "llama2")
            assert result == "test response"


class TestCompanyLLMIntegration:
    def test_company_set_llm_provider(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "ollama")
        company = Company()
        company.set_llm_provider()
        assert company.llm_provider is not None
        assert isinstance(company.llm_provider, OllamaProvider)

    def test_company_get_llm_provider(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "openrouter")
        company = Company()
        provider = company.get_llm_provider()
        assert isinstance(provider, OpenRouterProvider)

    def test_company_get_llm_provider_caches(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "github_copilot")
        company = Company()
        provider1 = company.get_llm_provider()
        provider2 = company.get_llm_provider()
        assert provider1 is provider2


class TestAgentLLMIntegration:
    def test_agent_set_llm_provider(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "ollama")
        agent = Agent(
            id="agent-1",
            name="Test Agent",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR
        )
        provider = get_provider()
        agent.set_llm_provider(provider)
        assert agent.llm_provider is provider

    def test_agent_complete_uses_provider(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "ollama")
        agent = Agent(
            id="agent-1",
            name="Test Agent",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR
        )
        provider = get_provider()
        agent.set_llm_provider(provider)
        
        with patch.object(provider, 'complete', return_value="test"):
            result = agent.complete("test prompt", model="llama2")
            assert result == "test"

    def test_agent_chat_uses_provider(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "ollama")
        agent = Agent(
            id="agent-1",
            name="Test Agent",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR
        )
        provider = get_provider()
        agent.set_llm_provider(provider)
        
        with patch.object(provider, 'chat', return_value="test"):
            messages = [{"role": "user", "content": "test"}]
            result = agent.chat(messages, model="llama2")
            assert result == "test"

    def test_agent_complete_no_provider_raises(self):
        agent = Agent(
            id="agent-1",
            name="Test Agent",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR
        )
        with pytest.raises(Exception, match="No LLM provider configured"):
            agent.complete("test prompt")

    def test_agent_chat_no_provider_raises(self):
        agent = Agent(
            id="agent-1",
            name="Test Agent",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR
        )
        with pytest.raises(Exception, match="No LLM provider configured"):
            agent.chat([{"role": "user", "content": "test"}])