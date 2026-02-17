from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import settings

class LLMProvider(ABC):
    @abstractmethod
    def create_client(self, api_key: str, model: str, temperature: float) -> BaseChatModel:
        pass

class GroqProvider(LLMProvider):
    def create_client(self, api_key: str, model: str, temperature: float) -> BaseChatModel:
        return ChatGroq(api_key=api_key, model_name=model, temperature=temperature)

class OpenAIProvider(LLMProvider):
    def create_client(self, api_key: str, model: str, temperature: float) -> BaseChatModel:
        return ChatOpenAI(api_key=api_key, model=model, temperature=temperature)

class OpenRouterProvider(LLMProvider):
    def create_client(self, api_key: str, model: str, temperature: float) -> BaseChatModel:
        return ChatOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model=model,
            temperature=temperature
        )

class GeminiProvider(LLMProvider):
    def create_client(self, api_key: str, model: str, temperature: float) -> BaseChatModel:
        return ChatGoogleGenerativeAI(google_api_key=api_key, model=model, temperature=temperature)

class LLMFactory:
    """Factory to create LLM clients based on configuration"""
    
    PROVIDERS = {
        "groq": GroqProvider(),
        "openai": OpenAIProvider(),
        "openrouter": OpenRouterProvider(),
        "gemini": GeminiProvider()
    }
    
    @classmethod
    def create_llm(cls) -> Optional[BaseChatModel]:
        config = settings.config.llm
        if not config.api_key:
            return None
            
        provider = cls.PROVIDERS.get(config.provider.lower())
        if not provider:
            raise ValueError(f"Unsupported provider: {config.provider}")
            
        return provider.create_client(
            api_key=config.api_key,
            model=config.model_name,
            temperature=config.temperature
        )
