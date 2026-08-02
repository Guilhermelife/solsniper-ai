from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SolSniper AI API"
    version: str = "0.1.0"
    environment: str = "development"


settings = Settings()