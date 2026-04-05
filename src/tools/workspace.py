import os
import subprocess
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Workspace:
    repo_url: str
    branch: str
    path: str
    agent_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_initialized: bool = False

    def initialize(self) -> bool:
        try:
            if os.path.exists(self.path):
                subprocess.run(["git", "fetch"], cwd=self.path, capture_output=True)
            else:
                subprocess.run(["git", "clone", self.repo_url, self.path], capture_output=True)
            
            subprocess.run(["git", "checkout", self.branch], cwd=self.path, capture_output=True)
            self.is_initialized = True
            return True
        except Exception:
            return False

    def checkout_branch(self) -> bool:
        try:
            subprocess.run(["git", "fetch"], cwd=self.path, capture_output=True)
            result = subprocess.run(
                ["git", "checkout", "-b", self.branch],
                cwd=self.path,
                capture_output=True,
                text=True
            )
            if result.returncode != 0 and "already exists" in result.stderr:
                subprocess.run(["git", "checkout", self.branch], cwd=self.path, capture_output=True)
            return True
        except Exception:
            return False

    def commit_changes(self, message: str) -> bool:
        try:
            subprocess.run(["git", "add", "."], cwd=self.path, capture_output=True)
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def push_branch(self, remote: str = "origin") -> bool:
        try:
            result = subprocess.run(
                ["git", "push", "-u", remote, self.branch],
                cwd=self.path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def cleanup(self) -> bool:
        try:
            if os.path.exists(self.path):
                import shutil
                shutil.rmtree(self.path)
            return True
        except Exception:
            return False

    def get_status(self) -> dict:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.path,
                capture_output=True,
                text=True
            )
            return {
                "branch": self.branch,
                "has_changes": bool(result.stdout.strip()),
                "changes": result.stdout.strip().split('\n') if result.stdout.strip() else []
            }
        except Exception:
            return {"branch": self.branch, "has_changes": False, "changes": []}