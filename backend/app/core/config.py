"""Configuración transversal de la aplicación (una sola fuente de settings para todos los módulos)."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Piedrazul - Monolito Modular"
    # SQLite por defecto para poder levantar el proyecto sin instalar nada más.
    # En despliegue se usa PostgreSQL (un schema por módulo) vía la variable DATABASE_URL:
    # postgresql+psycopg2://postgres:postgres@localhost:5432/piedrazul
    database_url: str = "sqlite:///./piedrazul.db"
    cors_origins: list[str] = ["http://localhost:4200"]
    jwt_secret: str = "change-me"  # TODO: reemplazar por Keycloak/JWT real en el Corte 2
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
