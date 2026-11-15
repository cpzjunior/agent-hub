
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnthropicSettings(BaseSettings):
    model: str = "claude-sonnet-4-5"
    api_key: SecretStr | None = None
    temperature: float = 0.0

    model_config = SettingsConfigDict(
        env_prefix="ANTHROPIC_",
        env_file=".env",
        extra="ignore",
    )
