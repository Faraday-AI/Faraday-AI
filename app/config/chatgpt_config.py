from pydantic import BaseSettings
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class ChatGPTConfig(BaseSettings):
    # OpenAI API Configuration
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # System Messages for Different Contexts
    system_prompts: Dict[str, str] = {
        "default": "You are an AI teaching assistant helping with Physical Education curriculum development.",
        "lesson_plan": "You are an AI curriculum specialist focused on creating detailed PE lesson plans.",
        "assessment": "You are an AI assessment specialist helping create PE evaluation criteria.",
        "adaptation": "You are an AI specialist in adapting PE activities for different ability levels."
    }
    
    # Beta Phase Settings
    is_beta: bool = os.getenv("APP_ENVIRONMENT") == "beta"
    debug_mode: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Response Configuration
    stream_response: bool = True
    include_citations: bool = True
    
    class Config:
        env_file = ".env"

chatgpt_settings = ChatGPTConfig() 