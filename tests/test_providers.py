import pytest
from unittest.mock import Mock, patch
from src.providers import LLMProvider, get_provider
from src.providers.openrouter import OpenRouterProvider
from src.providers.github_copilot import GitHubCopilotProvider
from src.providers.kilo_gateway import KiloGatewayProvider
from src.models.company import Company
from src.models.agent import Agent
from src.models.enums import AgentRole, AgentLevel


class TestLLMProvider:
    def test_provider_name_property(self):
        class TestProvider(LLMProvider):
            @property
            def provider_name(self) -> str:
                return "test"
            
            def complete(self, prompt: str, model: str, **kwargs) -> str:
                return "test response"
            
            def chat(self, messages: list, model: str, **kwargs) -> str:
                return "test response"
        
        provider = TestProvider()
        assert provider.provider_name == "test"
    
    def test_complete_not_implemented(self):
        class TestProvider(LLMProvider):
            @property
            def provider_name(self) -> str:
                return "test"
        
        provider = TestProvider()
        with pytest.raises(TypeError):
            provider.complete("test prompt", "gpt-3.5-turbo")
    
    def test_chat_not_implemented(self):
        class TestProvider(LLMProvider):
            @property
            def provider_name(self) -> str:
                return "test"
        
        provider = TestProvider()
        with pytest.raises(TypeError):
            provider.chat([{"role": "user", "content": "test"}], "gpt-3.5-turbo")


class TestOpenRouterProvider:
    def test_provider_name(self):
        provider = OpenRouterProvider(api_key="test-key")
        assert provider.provider_name == "openrouter"
    
    def test_default_base_url(self):
        provider = OpenRouterProvider(api_key="test-key")
        assert provider.base_url == "https://openrouter.ai/api/v1"
    
    def test_custom_base_url(self):
        provider = OpenRouterProvider(api_key="test-key", base_url="https://custom.example.com")
        assert provider.base_url == "https://custom.example.com"
    
    @patch("src.providers.openrouter.requests.post")
    def test_complete(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        provider = OpenRouterProvider(api_key="test-key")
        result = provider.complete("Hello", "gpt-3.5-turbo")
        
        assert result == "Test response"
        mock_post.assert_called_once()
    
    @patch("src.providers.openrouter.requests.post")
    def test_chat(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Chat response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        provider = OpenRouterProvider(api_key="test-key")
        messages = [{"role": "user", "content": "Hello"}]
        result = provider.chat(messages, "gpt-4")
        
        assert result == "Chat response"
        mock_post.assert_called_once()


class TestGitHubCopilotProvider:
    def test_provider_name(self):
        provider = GitHubCopilotProvider(api_key="test-key")
        assert provider.provider_name == "github_copilot"
    
    def test_default_base_url(self):
        provider = GitHubCopilotProvider(api_key="test-key")
        assert provider.base_url == "https://api.github.com/copilot"
    
    def test_custom_base_url(self):
        provider = GitHubCopilotProvider(api_key="test-key", base_url="https://custom.example.com/copilot")
        assert provider.base_url == "https://custom.example.com/copilot"
    
    @patch("src.providers.github_copilot.requests.post")
    def test_complete(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Copilot response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        provider = GitHubCopilotProvider(api_key="test-key")
        result = provider.complete("Hello", "gpt-4")
        
        assert result == "Copilot response"
    
    @patch("src.providers.github_copilot.requests.post")
    def test_chat(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Copilot chat response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        provider = GitHubCopilotProvider(api_key="test-key")
        messages = [{"role": "user", "content": "Hello"}]
        result = provider.chat(messages, "gpt-4")
        
        assert result == "Copilot chat response"


class TestKiloGatewayProvider:
    def test_provider_name(self):
        provider = KiloGatewayProvider(api_key="test-key")
        assert provider.provider_name == "kilo_gateway"
    
    def test_default_base_url(self):
        provider = KiloGatewayProvider(api_key="test-key")
        assert provider.base_url == "https://gateway.kilo.ai/v1"
    
    def test_custom_base_url(self):
        provider = KiloGatewayProvider(api_key="test-key", base_url="https://custom.example.com/v1")
        assert provider.base_url == "https://custom.example.com/v1"
    
    @patch("src.providers.kilo_gateway.requests.post")
    def test_complete(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Kilo response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        provider = KiloGatewayProvider(api_key="test-key")
        result = provider.complete("Hello", "kilo-default")
        
        assert result == "Kilo response"
    
    @patch("src.providers.kilo_gateway.requests.post")
    def test_chat(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Kilo chat response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        provider = KiloGatewayProvider(api_key="test-key")
        messages = [{"role": "user", "content": "Hello"}]
        result = provider.chat(messages, "kilo-default")
        
        assert result == "Kilo chat response"


class TestProviderFactory:
    @patch("src.providers.openrouter.OpenRouterProvider")
    def test_get_default_provider(self, mock_provider):
        from src.providers import get_provider
        provider = get_provider("openrouter")
        assert provider is not None
    
    @patch("src.providers.github_copilot.GitHubCopilotProvider")
    def test_get_github_copilot_provider(self, mock_provider):
        from src.providers import get_provider
        provider = get_provider("github_copilot")
        assert provider is not None
    
    @patch("src.providers.kilo_gateway.KiloGatewayProvider")
    def test_get_kilo_gateway_provider(self, mock_provider):
        from src.providers import get_provider
        provider = get_provider("kilo_gateway")
        assert provider is not None
    
    def test_get_provider_from_env_var(self, monkeypatch):
        monkeypatch.setenv("COMPANY_LLM_PROVIDER", "openrouter")
        from src.providers import get_provider
        provider = get_provider()
        assert provider is not None


class TestCompanyProvider:
    def test_company_has_default_provider(self):
        company = Company()
        assert company.llm_provider is not None
    
    def test_set_llm_provider(self):
        company = Company()
        new_provider = OpenRouterProvider(api_key="new-key")
        company.set_llm_provider(new_provider)
        assert company.llm_provider is new_provider
    
    @patch("src.providers.openrouter.requests.post")
    def test_company_complete(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Company completion"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        company = Company()
        company.llm_provider = OpenRouterProvider(api_key="test-key")
        result = company.complete("Test prompt", "gpt-3.5-turbo")
        
        assert result == "Company completion"
    
    @patch("src.providers.openrouter.requests.post")
    def test_company_chat(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Company chat"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        company = Company()
        company.llm_provider = OpenRouterProvider(api_key="test-key")
        messages = [{"role": "user", "content": "Hello"}]
        result = company.chat(messages, "gpt-3.5-turbo")
        
        assert result == "Company chat"
    
    def test_complete_without_provider(self):
        company = Company()
        company.llm_provider = None
        with pytest.raises(ValueError, match="No LLM provider configured"):
            company.complete("test", "gpt-3.5-turbo")
    
    def test_chat_without_provider(self):
        company = Company()
        company.llm_provider = None
        with pytest.raises(ValueError, match="No LLM provider configured"):
            company.chat([{"role": "user", "content": "test"}], "gpt-3.5-turbo")


class TestAgentProvider:
    @patch("src.providers.openrouter.requests.post")
    def test_agent_complete(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Agent completion"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        agent = Agent(
            id="agent-1",
            name="Test Agent",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR
        )
        company = Company()
        company.llm_provider = OpenRouterProvider(api_key="test-key")
        
        result = agent.complete(company, "Test prompt", "gpt-3.5-turbo")
        
        assert result == "Agent completion"
    
    @patch("src.providers.openrouter.requests.post")
    def test_agent_chat(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Agent chat"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        agent = Agent(
            id="agent-1",
            name="Test Agent",
            role=AgentRole.DEVELOPER,
            level=AgentLevel.JUNIOR
        )
        company = Company()
        company.llm_provider = OpenRouterProvider(api_key="test-key")
        
        messages = [{"role": "user", "content": "Hello"}]
        result = agent.chat(company, messages, "gpt-3.5-turbo")
        
        assert result == "Agent chat"