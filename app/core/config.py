from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Nexa Client´s Context Analizer API"
    debug: bool = True
    version: str = "0.1.0"

    # Pydantic v2 style configuration
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
