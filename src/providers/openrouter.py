import os
from typing import Dict, List
import urllib.request
import urllib.error
import json

from . import LLMProvider


class OpenRouterProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def complete(self, prompt: str, model: str = "openai/gpt-3.5-turbo", **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model, **kwargs)

    def chat(self, messages: List[Dict[str, str]], model: str = "openai/gpt-3.5-turbo", **kwargs) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/company",
            "X-Title": "CompAIny"
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
            raise Exception(f"OpenRouter API error: {e.code} - {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"OpenRouter connection error: {e.reason}")