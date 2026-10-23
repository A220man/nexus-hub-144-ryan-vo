from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "nexus-hub"
    app_version: str = "1.0.0"
    database_url: str = "sqlite:///./nexus.db"
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_api_key: Optional[str] = None
    llm_provider: str = "openai-compatible"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: Optional[str] = None
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()