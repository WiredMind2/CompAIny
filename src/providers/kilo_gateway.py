import os
from typing import Dict, List
import urllib.request
import urllib.error
import json

from . import LLMProvider


class KiloGatewayProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("KILO_GATEWAY_API_KEY", "")
        self.base_url = os.getenv("KILO_GATEWAY_URL", "https://gateway.kilo.ai/v1/chat/completions")

    def complete(self, prompt: str, model: str = "claude-3-5-sonnet-20241022", **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model, **kwargs)

    def chat(self, messages: List[Dict[str, str]], model: str = "claude-3-5-sonnet-20241022", **kwargs) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        body = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        req = urllib.request.Request(
            self.base_url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise Exception(f"Kilo Gateway API error: {e.code} - {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Kilo Gateway connection error: {e.reason}")