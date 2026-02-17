from pydantic import BaseModel, Field
from src.core.llm.factory import LLMFactory
from src.core.config import settings
import platform
import json

class CommandResponse(BaseModel):
    command_nlp: str = Field(description="The natural language description of the command")
    command_shell: str = Field(description="The executable shell command")
    explanation: str = Field(description="Brief explanation of what the command does")
    is_safe: bool = Field(description="Whether the command is safe to execute without confirmation")

class LLMEngine:
    def __init__(self):
        self.llm = None
        self.initialize()
        
    def initialize(self):
        """Initialize or re-initialize the LLM client"""
        try:
            self.llm = LLMFactory.create_llm()
        except Exception as e:
            print(f"LLM Initialization Error: {e}")
            self.llm = None

    def generate_command(self, user_input: str) -> CommandResponse:
        if not self.llm:
            return CommandResponse(
                command_nlp=user_input,
                command_shell="",
                explanation="LLM not configured. Please check settings.",
                is_safe=True
            )
            
        system_os = platform.system()
        prompt = f"""
        You are a helpful Linux terminal assistant.
        Convert the user's natural language request into a valid {system_os} shell command.
        
        Return ONLY valid JSON matching this schema:
        {{
            "command_nlp": "...",
            "command_shell": "...",
            "explanation": "...",
            "is_safe": true/false
        }}
        
        - "is_safe": false if the command deletes files (rm), modifies system settings, kills processes (kill), or is otherwise destructive. True for read-only commands (ls, cat, grep).
        
        User request: {user_input}
        """
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content
            
            # Clean up markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            content = content.strip()
            data = json.loads(content)
            return CommandResponse(**data)
            
        except Exception as e:
            return CommandResponse(
                command_nlp=user_input,
                command_shell="",
                explanation=f"Error generating command: {str(e)}",
                is_safe=True
            )
