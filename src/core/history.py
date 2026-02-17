import json
import os
from typing import List, Dict
from datetime import datetime


class AliasManager:
    """Manages custom command aliases and macros"""
    
    def __init__(self, filepath: str = "command_aliases.json"):
        self.filepath = filepath
        self.aliases = self.load_aliases()
    
    def load_aliases(self) -> Dict[str, str]:
        """Load aliases from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_aliases(self):
        """Save aliases to file"""
        with open(self.filepath, 'w') as f:
            json.dump(self.aliases, f, indent=2)
    
    def add_alias(self, name: str, command: str):
        """Add or update an alias"""
        self.aliases[name] = command
        self.save_aliases()
    
    def remove_alias(self, name: str):
        """Remove an alias"""
        if name in self.aliases:
            del self.aliases[name]
            self.save_aliases()
    
    def get_command(self, name: str) -> str:
        """Get command for alias"""
        return self.aliases.get(name, "")
    
    def get_all_aliases(self) -> Dict[str, str]:
        """Get all aliases"""
        return self.aliases.copy()
    
    def expand_alias(self, text: str) -> str:
        """Expand alias in text if it matches"""
        for alias, command in self.aliases.items():
            if text.strip().lower() == alias.lower():
                return command
        return text


class CommandHistory:
    """Enhanced command history with search and autocomplete"""
    
    def __init__(self, filepath: str = "promptshell_history.json"):
        self.filepath = filepath
        self.history = self.load_history()
    
    def load_history(self) -> List[Dict]:
        """Load history from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Save history to file"""
        with open(self.filepath, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_entry(self, nlp: str, command: str, success: bool = True):
        """Add entry to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "nlp": nlp,
            "command": command,
            "success": success
        }
        self.history.insert(0, entry)  # Add to beginning
        
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[:100]
        
        self.save_history()
    
    def search(self, query: str) -> List[Dict]:
        """Search history by query"""
        query = query.lower()
        results = []
        for entry in self.history:
            # Handle both old and new format
            nlp = entry.get('nlp') or entry.get('command_nlp', '')
            cmd = entry.get('command') or entry.get('command_shell', '')
            
            if query in nlp.lower() or query in cmd.lower():
                results.append(entry)
        return results
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """Get recent entries"""
        return self.history[:count]
    
    def get_autocomplete_suggestions(self, prefix: str) -> List[str]:
        """Get autocomplete suggestions based on prefix"""
        suggestions = set()
        prefix = prefix.lower()
        
        for entry in self.history:
            # Handle both old and new format
            cmd = entry.get('command') or entry.get('command_shell', '')
            if not cmd:
                continue
                
            if cmd.lower().startswith(prefix):
                # Add the first word/command
                first_word = cmd.split()[0] if cmd.split() else cmd
                suggestions.add(first_word)
        
        # Add common commands
        common_commands = ['cd', 'ls', 'git', 'python', 'pip', 'npm', 'docker', 
                          'mkdir', 'rm', 'cp', 'mv', 'cat', 'grep', 'find', 'chmod']
        for cmd in common_commands:
            if cmd.startswith(prefix):
                suggestions.add(cmd)
        
        return sorted(list(suggestions))
    
    def clear(self):
        """Clear all history"""
        self.history = []
        self.save_history()
