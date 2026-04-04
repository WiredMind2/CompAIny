import os
import requests
from typing import List, Dict, Optional

from . import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama local API provider."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    @property
    def provider_name(self) -> str:
        return "ollama"
    
    def complete(self, prompt: str, model: str = "llama2", **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model, **kwargs)
    
    def chat(self, messages: List[Dict[str, str]], model: str = "llama2", **kwargs) -> str:
        payload = {
            "model": model,
            "messages": messages,
        }
        
        temperature = kwargs.get("temperature")
        if temperature is not None:
            payload["temperature"] = temperature
        
        timeout = kwargs.get("timeout", 60)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error: {e.response.status_code} - {e.response.text}")