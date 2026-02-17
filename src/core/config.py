import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    provider: str = "openrouter"
    model_name: str = "openai/gpt-oss-120b"
    api_key: str = ""
    temperature: float = 0.1

class AppConfig(BaseModel):
    theme: str = "dark"
    llm: LLMConfig = Field(default_factory=LLMConfig)
    history_limit: int = 1000

class ConfigManager:
    """Manages application configuration with persistence"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".promptshell"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        self.config = self.load_config()
        
    def ensure_config_dir(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
            
    def load_config(self) -> AppConfig:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    # Handle backward compatibility or missing fields
                    return AppConfig(**data)
            except Exception as e:
                print(f"Error loading config: {e}")
                return AppConfig()
        return AppConfig()
        
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.dict(), f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.config, key, default)
        
    def set(self, key: str, value: Any):
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
    
    def set_theme(self, theme: str):
        """Set application theme (light or dark)"""
        self.config.theme = theme
        self.save_config()
            
    def update_llm_config(self, provider: str, model: str, api_key: str):
        self.config.llm.provider = provider
        self.config.llm.model_name = model
        if api_key:  # Only update if provided
            self.config.llm.api_key = api_key
        self.save_config()

# Global config instance
settings = ConfigManager()
