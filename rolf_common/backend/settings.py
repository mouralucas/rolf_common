from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project description
    project_name: str = "Library Service Microservice"
    project_description: str = "This service contains all necessary functions to manage a library"
    project_version: str = "0.0.1"

    # Microservice comm settings
    auth_service_base_url: str = 'http://localhost:8001'

    log_database_name: str | None = None
    log_database_url: str | None = None

settings = Settings()
