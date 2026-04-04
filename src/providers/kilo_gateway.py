import os
import requests
from typing import List, Dict, Optional

from . import LLMProvider


class KiloGatewayProvider(LLMProvider):
    """Kilo Gateway API provider."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.environ.get("KILO_GATEWAY_API_KEY", "")
        self.base_url = base_url or os.environ.get("KILO_GATEWAY_URL", "https://gateway.kilo.ai/v1")
    
    @property
    def provider_name(self) -> str:
        return "kilo_gateway"
    
    def complete(self, prompt: str, model: str = "kilo-default", **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model, **kwargs)
    
    def chat(self, messages: List[Dict[str, str]], model: str = "kilo-default", **kwargs) -> str:
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
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