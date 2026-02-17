import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = "openai/gpt-oss-120b"
    
    @property
    def is_valid(self):
        return bool(self.GROQ_API_KEY)

settings = Settings()
