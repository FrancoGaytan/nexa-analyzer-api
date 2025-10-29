from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Nexa Client´s Context Analizer API"
    debug: bool = True
    version: str = "0.1.0"
    cors_origins: str | None = None  # Comma-separated origins e.g. "http://localhost:5173,http://127.0.0.1:5173"

    # Pydantic v2 style configuration
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

def get_cors_origin_list() -> list[str]:
    if not settings.cors_origins:
        # Default allow typical local dev ports (frontend vite + maybe 3000)
        return ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"];  
    return [o.strip() for o in settings.cors_origins.split(',') if o.strip()]
