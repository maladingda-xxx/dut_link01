from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, populated from environment variables (DUTLINK_ prefix)."""

    app_name: str = "dut-link-backend"
    debug: bool = False

    # PostgreSQL connection string (asyncpg driver). Override via DUTLINK_DATABASE_URL.
    database_url: str = "postgresql+asyncpg://dutlink:dutlink@localhost:5432/dutlink"

    # Comma-separated list of allowed CORS origins.
    cors_origins: str = "http://localhost:5173,http://localhost:4173"

    # DeepSeek (OpenAI-compatible chat API). Key is read directly from DEEPSEEK_API_KEY
    # (no DUTLINK_ prefix), matching the cc-switch convention.
    deepseek_api_key: str = Field(default="", validation_alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"

    # Local embedding model (sentence-transformers). Multilingual, 384-dim output.
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384

    model_config = SettingsConfigDict(
        env_prefix="DUTLINK_",
        env_file=".env",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
