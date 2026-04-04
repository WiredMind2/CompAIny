import os
from typing import Dict, List
import urllib.request
import urllib.error
import json

from . import LLMProvider


class GitHubCopilotProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GITHUB_COPILOT_TOKEN", "")
        self.base_url = "https://api.github.com/copilot/chat/completions"

    def complete(self, prompt: str, model: str = "gpt-4o", **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model, **kwargs)

    def chat(self, messages: List[Dict[str, str]], model: str = "gpt-4o", **kwargs) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.copilot-chat+json",
            "X-GitHub-Api-Version": "2022-11-28"
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
            raise Exception(f"GitHub Copilot API error: {e.code} - {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"GitHub Copilot connection error: {e.reason}")