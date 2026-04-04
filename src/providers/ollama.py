import os
import json
import urllib.request
import urllib.error
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
        
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["message"]["content"]
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")