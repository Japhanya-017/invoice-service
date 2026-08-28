from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

class Settings(BaseSettings):
    app_name: str
    app_version: str
    app_host: str
    app_port: int
    debug: bool

    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    api_gateway_url: str

    UPLOAD_DIR: str = "uploads/timesheets"
    EMPLOYEE_SERVICE_URL: str="http://localhost:8002"
    
    jwt_secret_key: str
    jwt_algorithm: str

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.database_user,
            password=self.database_password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )



@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()