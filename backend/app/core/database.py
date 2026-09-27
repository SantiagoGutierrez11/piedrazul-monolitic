"""
Sesión y engine de SQLAlchemy compartidos por todos los módulos.

Decisión de arquitectura (ver discusión de equipo): una sola instancia de base de
datos, con un schema por módulo (appointment, configuration, medical_staff, ...)
en lugar de una BD física por módulo como en los microservicios. Cada módulo solo
debe tocar su propio schema desde su capa de infraestructura.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

MODULE_SCHEMAS = ("appointment", "configuration", "medical_staff", "patient", "identity")

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# SQLite no tiene schemas; al usarlo todas las tablas caen en el schema por defecto.
SUPPORTS_SCHEMAS = engine.dialect.name != "sqlite"


def module_table_args(module: str, *args):
    """__table_args__ de un modelo, ubicándolo en el schema de su módulo cuando el motor lo soporta."""
    return (*args, {"schema": module} if SUPPORTS_SCHEMAS else {})


def get_db():
    """Dependency de FastAPI: entrega una sesión por request y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea los schemas de cada módulo y las tablas declaradas. Se llama al arrancar la app."""
    # Import local: registra los modelos en Base.metadata sin crear imports circulares.
    from app.modules.appointment.infrastructure import models as appointment_models  # noqa: F401
    from app.modules.configuration.infrastructure import models as configuration_models  # noqa: F401
    from app.modules.medical_staff.infrastructure import models as medical_staff_models  # noqa: F401
    from app.modules.patient.infrastructure import models as patient_models  # noqa: F401

    if SUPPORTS_SCHEMAS:
        with engine.begin() as connection:
            for schema in MODULE_SCHEMAS:
                connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

    Base.metadata.create_all(bind=engine)
