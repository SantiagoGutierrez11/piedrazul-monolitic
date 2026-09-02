"""
Seguridad transversal (JWT). Placeholder para el Corte 1.

En el Corte 2 esto se conecta a Keycloak (ver requisito no funcional de
autenticación/autorización de los entregables). Por ahora expone el shape
que los módulos ya pueden asumir para no tener que refactorizar después.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def get_current_user(token: str | None = Depends(oauth2_scheme)) -> dict:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    # TODO: decodificar/validar JWT real (Keycloak) en el Corte 2.
    return {"sub": "todo", "roles": []}


def require_role(*roles: str):
    def _checker(user: dict = Depends(get_current_user)) -> dict:
        if roles and not set(roles) & set(user.get("roles", [])):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        return user

    return _checker
