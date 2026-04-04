import os
from typing import Dict, List
import urllib.request
import urllib.error
import json

from . import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def complete(self, prompt: str, model: str = "llama2", **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model, **kwargs)

    def chat(self, messages: List[Dict[str, str]], model: str = "llama2", **kwargs) -> str:
        url = f"{self.base_url}/api/chat"

        body = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise Exception(f"Ollama API error: {e.code} - {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Ollama connection error: {e.reason}")