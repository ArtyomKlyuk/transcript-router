from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    vault_path: Path = Path("./vault")
    anthropic_api_key: SecretStr | None = None
    anthropic_model: str = "claude-opus-4-7"
    log_level: str = "INFO"
