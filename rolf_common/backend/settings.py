from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Microservice comm settings
    auth_service_base_url = 'localhost:8001'

    # Project description
    project_name: str = "Library Service Microservice"
    project_description: str = "This service contains all necessary functions to manage a library"
    project_version: str = "0.0.1"


settings = Settings()
