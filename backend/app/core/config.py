"""Configuración transversal de la aplicación (una sola fuente de settings para todos los módulos)."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Piedrazul - Monolito Modular"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/piedrazul"
    jwt_secret: str = "change-me"  # TODO: reemplazar por Keycloak/JWT real en el Corte 2
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
