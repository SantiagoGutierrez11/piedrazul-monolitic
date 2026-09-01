"""
Sesión y engine de SQLAlchemy compartidos por todos los módulos.

Decisión de arquitectura (ver discusión de equipo): una sola instancia de base de
datos, con un schema por módulo (appointment, configuration, medical_staff, ...)
en lugar de una BD física por módulo como en los microservicios. Cada módulo solo
debe tocar su propio schema desde su capa de infraestructura.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency de FastAPI: entrega una sesión por request y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
