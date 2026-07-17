from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    backend_cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="BACKEND_CORS_ORIGINS",
    )
    database_url: str = Field(default="", alias="DATABASE_URL")
    local_demo_mode: bool = Field(default=True, alias="LOCAL_DEMO_MODE")
    local_demo_database_url: str = Field(
        default="sqlite:///./.padalo-demo.sqlite3",
        alias="LOCAL_DEMO_DATABASE_URL",
    )
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5.6", alias="OPENAI_MODEL")
    demo_reset_enabled: bool = Field(default=False, alias="DEMO_RESET_ENABLED")
    demo_reset_token: str = Field(default="", alias="DEMO_RESET_TOKEN")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @property
    def uses_local_demo_database(self) -> bool:
        """Keep the no-setup demo available locally without weakening production configuration."""

        return (
            self.app_env.strip().lower() in {"development", "test"}
            and self.local_demo_mode
            and not self.database_url.strip()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
