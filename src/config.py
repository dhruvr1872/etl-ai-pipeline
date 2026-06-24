from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    database_url: str = Field(default="sqlite:///data/warehouse.db", env="DATABASE_URL")
    chroma_persist_dir: str = Field(default=".chroma", env="CHROMA_PERSIST_DIR")
    batch_size: int = Field(default=50, env="BATCH_SIZE")
    llm_model: str = Field(default="gpt-4o-mini", env="LLM_MODEL")
    news_api_key: str = Field(default="", env="NEWS_API_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
