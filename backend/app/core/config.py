"""Configuración transversal de la aplicación (una sola fuente de settings para todos los módulos)."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Piedrazul - Monolito Modular"
    # SQLite por defecto para poder levantar el proyecto sin instalar nada más.
    # En despliegue se usa PostgreSQL (un schema por módulo) vía la variable DATABASE_URL:
    # postgresql+psycopg2://postgres:postgres@localhost:5432/piedrazul
    database_url: str = "sqlite:///./piedrazul.db"
    cors_origins: list[str] = ["http://localhost:4200"]
    # Zona horaria del centro médico: "hoy" y "ahora" para las reglas de agendamiento.
    timezone: str = "America/Bogota"

    # Keycloak: el backend es el único que habla con él (login, registro y validación de tokens).
    # Dentro de docker-compose se sobrescribe con KEYCLOAK_URL=http://keycloak:8080.
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "piedrazul"
    keycloak_client_id: str = "piedrazul-backend"
    keycloak_client_secret: str = "piedrazul-backend-secret"

    @property
    def keycloak_issuer(self) -> str:
        return f"{self.keycloak_url}/realms/{self.keycloak_realm}"

    class Config:
        env_file = ".env"


settings = Settings()
