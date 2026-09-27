"""Excepciones de dominio comunes y su traducción a respuestas HTTP (equivalente a los *ExceptionHandler de Spring)."""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
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


class AuthenticationError(DomainError):
    """Credenciales o token inválidos."""


class ForbiddenError(DomainError):
    """El usuario está autenticado pero su rol no le permite la operación."""


class ServiceUnavailableError(DomainError):
    """Un servicio externo del que dependemos (p. ej. Keycloak) no responde."""


def register_exception_handlers(app) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(_: Request, exc: RequestValidationError):
        # No se devuelve el cuerpo recibido (la respuesta por defecto lo incluye): puede traer contraseñas.
        errors = [
            {
                "field": ".".join(str(part) for part in error["loc"][1:]),
                "message": error["msg"].removeprefix("Value error, "),
            }
            for error in exc.errors()
        ]
        message = errors[0]["message"] if errors else "Los datos enviados no son válidos"
        return JSONResponse(status_code=422, content={"message": message, "errors": errors})

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"message": exc.message})

    @app.exception_handler(ValidationError)
    async def validation_handler(_: Request, exc: ValidationError):
        return JSONResponse(status_code=400, content={"message": exc.message})

    @app.exception_handler(ConflictError)
    async def conflict_handler(_: Request, exc: ConflictError):
        return JSONResponse(status_code=409, content={"message": exc.message})

    @app.exception_handler(AuthenticationError)
    async def authentication_handler(_: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=401,
            content={"message": exc.message},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(_: Request, exc: ForbiddenError):
        return JSONResponse(status_code=403, content={"message": exc.message})

    @app.exception_handler(ServiceUnavailableError)
    async def unavailable_handler(_: Request, exc: ServiceUnavailableError):
        return JSONResponse(status_code=503, content={"message": exc.message})
