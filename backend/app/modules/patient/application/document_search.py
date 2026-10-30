"""
Búsqueda de pacientes por número de cédula para consultar su historial de citas (E7-HU1).

El personal escribe la cédula tal como aparece en el documento del paciente. Mientras escribe,
la pantalla le sugiere pacientes cuya cédula empieza por lo que lleva escrito.
"""
import re

from app.core.exceptions import ValidationError
from app.core.security import Role
from app.modules.patient.domain.entities import Patient
from app.modules.patient.infrastructure.repository import PatientRepository

# ---------------------------------------------------------------- Formato de la cédula (2.1)

# Solo dígitos: sin puntos, letras, espacios ni guiones. El registro de pacientes acepta
# documentos desde 5 caracteres; una cédula colombiana tiene como máximo 10 dígitos.
MIN_DIGITS = 5
MAX_DIGITS = 10
_DIGITS = re.compile(r"\d+")

# El autocompletado se activa desde el tercer dígito: con menos, casi todos los pacientes
# coincidirían y la lista no ayudaría a encontrar a nadie.
MIN_DIGITS_TO_SUGGEST = 3
MAX_SUGGESTIONS = 8

INVALID_FORMAT = "La cédula solo puede tener números, sin puntos, letras ni espacios"
TOO_LONG = f"La cédula tiene como máximo {MAX_DIGITS} dígitos"
TOO_SHORT = f"Escribe la cédula completa: tiene al menos {MIN_DIGITS} dígitos"


def _validated(text: str) -> str:
    """La cédula sin espacios alrededor, o `ValidationError` si no tiene el formato válido."""
    document = text.strip()
    if not _DIGITS.fullmatch(document):
        raise ValidationError(INVALID_FORMAT)
    if len(document) > MAX_DIGITS:
        raise ValidationError(TOO_LONG)
    return document


def suggestion_prefix(text: str) -> str | None:
    """
    Inicio de cédula con el que se buscan sugerencias, o `None` si todavía es muy corto para
    sugerir (la pantalla muestra entonces la ayuda en lugar de la lista).
    """
    prefix = _validated(text)
    return prefix if len(prefix) >= MIN_DIGITS_TO_SUGGEST else None


def full_document(text: str) -> str:
    """Cédula completa para la búsqueda exacta (botón Buscar)."""
    document = _validated(text)
    if len(document) < MIN_DIGITS:
        raise ValidationError(TOO_SHORT)
    return document


# ---------------------------------------------------------------- Búsqueda (3.1)

# Los mismos roles que consultan el historial de citas (subtarea 2.3, ver
# appointment/application/patient_history.py): el paciente no busca a otros pacientes.
SEARCH_ROLES = (Role.MEDICO, Role.AGENDADOR, Role.ADMINISTRADOR)


class SearchPatientsByDocument:
    def __init__(self, repository: PatientRepository):
        self._repository = repository

    def execute(self, text: str) -> list[Patient]:
        """
        Pacientes cuya cédula empieza por lo escrito, con la coincidencia exacta primero.
        Con menos de 3 dígitos devuelve una lista vacía: todavía no se sugiere nada.
        """
        prefix = suggestion_prefix(text)
        if prefix is None:
            return []
        return self._repository.find_by_document_prefix(prefix, MAX_SUGGESTIONS)
