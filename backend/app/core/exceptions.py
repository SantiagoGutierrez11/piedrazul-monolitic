"""Excepciones de dominio comunes y su traducción a respuestas HTTP (equivalente a los *ExceptionHandler de Spring)."""
from fastapi import Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Excepción base de dominio. Cada módulo puede extenderla (p. ej. AppointmentConflictError)."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class ConflictError(DomainError):
    pass


def register_exception_handlers(app) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"message": exc.message})

    @app.exception_handler(ValidationError)
    async def validation_handler(_: Request, exc: ValidationError):
        return JSONResponse(status_code=400, content={"message": exc.message})

    @app.exception_handler(ConflictError)
    async def conflict_handler(_: Request, exc: ConflictError):
        return JSONResponse(status_code=409, content={"message": exc.message})
