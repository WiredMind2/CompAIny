import os
import requests
from typing import List, Dict, Optional

from . import LLMProvider


class GitHubCopilotProvider(LLMProvider):
    """GitHub Copilot API provider."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.github.com/copilot"):
        self.api_key = api_key or os.environ.get("GITHUB_COPILOT_API_KEY", "")
        self.base_url = base_url
    
    @property
    def provider_name(self) -> str:
        return "github_copilot"
    
    def complete(self, prompt: str, model: str = "gpt-4", **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model, **kwargs)
    
    def chat(self, messages: List[Dict[str, str]], model: str = "gpt-4", **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.copilot-preview+json",
        }
        
        payload = {
            "model": model,
            "messages": messages,
        }
        
        max_tokens = kwargs.get("max_tokens")
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        temperature = kwargs.get("temperature")
        if temperature is not None:
            payload["temperature"] = temperature
        
        timeout = kwargs.get("timeout", 60)
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error: {e.response.status_code} - {e.response.text}")