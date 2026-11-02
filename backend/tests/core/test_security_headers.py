"""Cabeceras de seguridad que el backend agrega a todas las respuestas (hallazgo de OWASP ZAP)."""


def test_successful_response_includes_nosniff(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_error_response_includes_nosniff(client):
    response = client.get("/ruta-que-no-existe")

    assert response.status_code == 404
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_unauthenticated_response_includes_nosniff(client, real_tokens):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["X-Content-Type-Options"] == "nosniff"
