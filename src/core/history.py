import json
import os
from datetime import datetime
from typing import List, Dict

class HistoryManager:
    def __init__(self, filepath="history.json"):
        self.filepath = filepath
        self.history: List[Dict] = self.load_history()

    def load_history(self) -> List[Dict]:
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def add_entry(self, nlp_command: str, shell_command: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "nlp": nlp_command,
            "shell": shell_command
        }
        self.history.append(entry)
        self._save()

    def _save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"Error saving history: {e}")

    def get_recent(self, limit=10):
        return self.history[-limit:]
