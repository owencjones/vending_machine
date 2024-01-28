from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vending Machine"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    database_url: str = "sqlite:///./vending_machine.db"
    jwt_secret: str
    jwt_timeout: int = 3600
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
