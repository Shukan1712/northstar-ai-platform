from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Northstar AI Decision Intelligence Platform"
    app_secret: str = "local-northstar-demo-secret"
    database_url: str = "postgresql+psycopg://northstar:northstar@localhost:5434/northstar"
    cors_origins: str = "http://localhost:4173,http://localhost:5173"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    ai_chat_model: str = ""
    ai_embedding_model: str = ""
    ai_max_tool_rounds: int = 4
    ai_daily_user_quota: int = 15
    ai_daily_global_quota: int = 75

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def ai_enabled(self) -> bool:
        return bool(self.openai_api_key.strip() and self.ai_chat_model.strip())

    @property
    def embeddings_enabled(self) -> bool:
        return bool(self.openai_api_key.strip() and self.ai_embedding_model.strip())

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        """Use psycopg 3 when a hosting provider supplies a generic Postgres URL."""
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
