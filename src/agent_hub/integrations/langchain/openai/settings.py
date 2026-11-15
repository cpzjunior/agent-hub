from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAISettings(BaseSettings):
    model: str = "gpt-4.1-mini"
    api_key: SecretStr | None = None
    temperature: float = 0.0

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        env_file=".env",
        extra="ignore",
    )