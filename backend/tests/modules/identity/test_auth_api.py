"""Pruebas del inicio, renovación y cierre de sesión."""
from app.core.security import Role


def _login(client, email, password):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_login_returns_tokens_and_user_roles(client, identity_provider):
    user_id = identity_provider.add_user(
        "admin@piedrazul.com", "admin123", Role.ADMINISTRADOR, first_name="Admin", last_name="Sistema"
    )

    response = _login(client, "  Admin@Piedrazul.com ", "admin123")

    assert response.status_code == 200
    body = response.json()
    assert body["user"] == {
        "id": user_id,
        "email": "admin@piedrazul.com",
        "fullName": "Admin Sistema",
        "roles": ["administrador"],
    }
    assert body["accessToken"] and body["refreshToken"]
    assert body["expiresIn"] == 300


def test_login_with_wrong_password_is_rejected(client, identity_provider):
    identity_provider.add_user("admin@piedrazul.com", "admin123", Role.ADMINISTRADOR)

    response = _login(client, "admin@piedrazul.com", "otra-clave")

    assert response.status_code == 401
    assert response.json() == {"message": "Correo o contraseña incorrectos"}


def test_refresh_issues_a_new_session(client, identity_provider):
    identity_provider.add_user("agendador@piedrazul.com", "agendador123", Role.AGENDADOR)
    refresh_token = _login(client, "agendador@piedrazul.com", "agendador123").json()["refreshToken"]

    response = client.post("/api/v1/auth/refresh", json={"refreshToken": refresh_token})

    assert response.status_code == 200
    assert response.json()["user"]["roles"] == ["agendador"]


def test_me_returns_the_authenticated_user(client, identity_provider):
    identity_provider.add_user("medico@piedrazul.com", "medico123", Role.MEDICO)
    token = _login(client, "medico@piedrazul.com", "medico123").json()["accessToken"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["roles"] == ["medico"]


def test_logout_closes_the_session_in_the_identity_provider(client, identity_provider):
    identity_provider.add_user("paciente@piedrazul.com", "paciente123", Role.PACIENTE)
    refresh_token = _login(client, "paciente@piedrazul.com", "paciente123").json()["refreshToken"]

    response = client.post("/api/v1/auth/logout", json={"refreshToken": refresh_token})

    assert response.status_code == 204
    assert identity_provider.logged_out == [refresh_token]
