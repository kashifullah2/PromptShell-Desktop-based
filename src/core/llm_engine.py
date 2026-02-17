from pydantic import BaseModel, Field
from src.core.llm.factory import LLMFactory
from src.core.config import settings
import platform
import json
from typing import Union, Dict, Any

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

    def process_query(self, user_input: str, task_type: str = "command") -> Union[CommandResponse, Dict[str, Any], str]:
        if not self.llm:
            if task_type == "command":
                return CommandResponse(
                    command_nlp=user_input,
                    command_shell="",
                    explanation="LLM not configured. Please check settings.",
                    is_safe=True
                )
            else:
                return "LLM not configured."
            
        try:
            if task_type == "analyst":
                return self._process_analyst(user_input)
            elif task_type == "developer":
                return self._process_developer(user_input)
            else:
                return self._process_command(user_input)
                
        except Exception as e:
            if task_type == "command":
                return CommandResponse(
                    command_nlp=user_input,
                    command_shell="",
                    explanation=f"Error generating response: {str(e)}",
                    is_safe=True
                )
            else:
                return f"Error: {str(e)}"

    def _process_command(self, user_input: str) -> CommandResponse:
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
        response = self.llm.invoke(prompt)
        return self._parse_json_response(response.content)

    def _process_analyst(self, user_input: str) -> Dict[str, Any]:
        # The user input already contains the context and the system prompt injection from TerminalWidget
        # We just need to enforce JSON output for the table structure
        
        # However, TerminalWidget injects "You are an expert Data Analyst..." into the query string.
        # Ideally, we should use a system message if the LLM supports it, but here we just append to prompt.
        
        response = self.llm.invoke(user_input)
        content = response.content
        
        # Clean up markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON array/object if present
            import re
            match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
            return {"error": "Could not parse JSON", "raw_content": content}

    def _process_developer(self, user_input: str) -> str:
        # User input has context. Developer mode returns Clean Code.
        response = self.llm.invoke(user_input)
        content = response.content
        
        # Clean up markdown code blocks to return just code
        if "```" in content:
            parts = content.split("```")
            if len(parts) >= 2:
                # usually parts[1] is the code, parts[0] is intro
                code_block = parts[1]
                # remove language identifier if present (e.g. "python\n")
                if "\n" in code_block:
                    first_line = code_block.split('\n')[0].strip()
                    if first_line and not first_line.startswith("#") and not first_line.startswith("//"):
                         # likely language identifier like "javascript" or "python"
                         code_block = code_block[len(first_line)+1:]
                return code_block.strip()
        
        return content.strip()

    def _parse_json_response(self, content: str) -> CommandResponse:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        content = content.strip()
        data = json.loads(content)
        return CommandResponse(**data)

    # Legacy alias
    def generate_command(self, user_input: str) -> CommandResponse:
        return self.process_query(user_input, "command")
