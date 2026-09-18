"""DTOs de entrada/salida de /api/v1/medical."""
from app.shared.schemas import CamelModel


class DoctorResponse(CamelModel):
    doctor_id: int
    full_name: str
    specialty: str
