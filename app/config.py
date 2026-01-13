from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database
    database_url: str = "sqlite:///./conflict_monitor.db"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production-use-env-variable"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()