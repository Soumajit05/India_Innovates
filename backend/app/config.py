from __future__ import annotations

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    app_name: str = "ARGOS"
    api_prefix: str = "/api"
    env: str = "development"
    debug: bool = False
    use_in_memory_graph: bool = True

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    redis_url: str = "redis://localhost:6379/0"
    frontend_url: str = "http://localhost:3000"
    secret_key: str = "dev-secret"

    anthropic_api_key: str | None = None
    argos_api_key: str = "argos-demo-key"
    twitter_bearer_token: str | None = None

    worldbank_api_base: str = "https://api.worldbank.org/v2"
    gdelt_api_base: str = "http://api.gdeltproject.org/api/v2/doc/doc"

    scheduler_interval_minutes: int = 15
    recompute_interval_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
