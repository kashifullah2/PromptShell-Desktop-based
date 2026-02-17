from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from src.core.config import settings
import platform
import json

class Command(BaseModel):
    command_nlp: str = Field(description="The natural language description of the command")
    command_shell: str = Field(description="The executable shell command")
    explanation: str = Field(description="Brief explanation of what the command does")
    is_safe: bool = Field(description="Whether the command is safe to execute without confirmation (e.g., ls, echo are safe; rm, dd are not)")

class LLMEngine:
    def __init__(self):
        if not settings.is_valid:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
            
        self.llm = ChatGroq(
            model=settings.MODEL_NAME,
            api_key=settings.GROQ_API_KEY,
            temperature=0.1 
        )

    def generate_command(self, user_input: str) -> Command:
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
        
        - "is_safe": false if the command deletes files (rm), modifies system settings, kills processes, or is otherwise destructive. True for read-only commands (ls, cat, grep).
        
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
            
            # Remove any leading/trailing whitespace or non-json characters if possible
            content = content.strip()
            
            data = json.loads(content)
            return Command(**data)
        except (json.JSONDecodeError, ValueError) as e:
            return Command(
                command_nlp=user_input,
                command_shell="",
                explanation=f"Error parsing command: {str(e)}",
                is_safe=True
            )
        except Exception as e:
            return Command(
                command_nlp=user_input,
                command_shell="",
                explanation=f"Error generating command: {str(e)}",
                is_safe=True
            )
