"""Punto de entrada del monolito modular: crea la app y monta el router de cada módulo."""
from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.modules.appointment.api.routes import router as appointment_router
from app.modules.configuration.api.routes import router as configuration_router
from app.modules.medical_staff.api.routes import router as medical_staff_router
from app.modules.patient.api.routes import router as patient_router
from app.modules.identity.api.routes import router as identity_router

app = FastAPI(title=settings.app_name)
register_exception_handlers(app)

app.include_router(appointment_router, prefix="/api/v1/appointments", tags=["Appointments"])
app.include_router(configuration_router, prefix="/api/v1/configuration", tags=["Configuration"])
app.include_router(medical_staff_router, prefix="/api/v1/medical", tags=["Medical Staff"])
app.include_router(patient_router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(identity_router, prefix="/api/v1/identity", tags=["Identity"])


@app.get("/health")
def health():
    return {"status": "ok"}
