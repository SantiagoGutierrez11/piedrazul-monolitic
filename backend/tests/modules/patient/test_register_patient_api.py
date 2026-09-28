"""Pruebas del registro de pacientes y de la consulta del perfil propio."""
from datetime import date, timedelta

from app.core.exceptions import ConflictError
from app.core.security import Role
from app.modules.patient.domain.entities import DocumentType, Patient
from app.modules.patient.infrastructure.repository import PatientRepository

URL = "/api/v1/patients/register"


def _registration(**overrides) -> dict:
    data = {
        "firstName": "María",
        "middleName": "Fernanda",
        "lastName": "Gómez",
        "secondLastName": "Rodríguez",
        "email": "maria.gomez@correo.com",
        "phone": "300 123 4567",
        "birthDate": "1958-04-12",
        "gender": "FEMENINO",
        "documentType": "CC",
        "documentNumber": "1023456789",
        "password": "clave1234",
        "confirmPassword": "clave1234",
    }
    data.update(overrides)
    return data


def test_registers_patient_with_a_paciente_account(client, identity_provider, db_session):
    response = client.post(URL, json=_registration())

    assert response.status_code == 201
    body = response.json()
    assert body["fullName"] == "María Fernanda Gómez Rodríguez"
    assert body["email"] == "maria.gomez@correo.com"

    [(user_id, (account, role))] = identity_provider.users.items()
    assert role == Role.PACIENTE
    assert (account.first_name, account.last_name) == ("María Fernanda", "Gómez Rodríguez")

    patient = PatientRepository(db_session).find_by_user_id(user_id)
    assert patient.patient_id == body["patientId"]
    assert patient.phone == "3001234567"
    assert patient.document_type == DocumentType.CC


def test_registered_patient_can_log_in_and_read_own_profile(client, identity_provider):
    client.post(URL, json=_registration())
    login = client.post(
        "/api/v1/auth/login", json={"email": "maria.gomez@correo.com", "password": "clave1234"}
    )

    response = client.get(
        "/api/v1/patients/me", headers={"Authorization": f"Bearer {login.json()['accessToken']}"}
    )

    assert login.json()["user"]["roles"] == ["paciente"]
    assert response.status_code == 200
    assert response.json()["documentNumber"] == "1023456789"


def test_passwords_must_match(client, identity_provider):
    response = client.post(URL, json=_registration(confirmPassword="otra-clave"))

    assert response.status_code == 422
    assert response.json()["message"] == "Las contraseñas no coinciden"
    assert "clave1234" not in response.text
    assert not identity_provider.users


def test_invalid_phone_is_rejected(client, identity_provider):
    response = client.post(URL, json=_registration(phone="12ab"))

    assert response.status_code == 422
    assert not identity_provider.users


def test_birth_date_cannot_be_in_the_future(client, identity_provider):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    response = client.post(URL, json=_registration(birthDate=tomorrow))

    assert response.status_code == 400
    assert not identity_provider.users


def test_email_already_registered_is_rejected_before_creating_account(client, identity_provider, db_session):
    PatientRepository(db_session).save(
        Patient(first_name="Otra", last_name="Persona", phone="3000000000", email="maria.gomez@correo.com")
    )

    response = client.post(URL, json=_registration(email="Maria.Gomez@correo.com"))

    assert response.status_code == 409
    assert response.json() == {"message": "Ya existe una cuenta registrada con ese correo electrónico"}
    assert not identity_provider.users


def test_document_already_registered_is_rejected(client, identity_provider):
    client.post(URL, json=_registration())

    response = client.post(URL, json=_registration(email="otro@correo.com"))

    assert response.status_code == 409
    assert response.json() == {"message": "Ya existe un paciente registrado con ese documento"}
    assert len(identity_provider.users) == 1


def test_account_conflict_in_identity_provider_does_not_create_patient(client, identity_provider, db_session):
    identity_provider.fail_create_with = ConflictError("Ya existe una cuenta registrada con ese correo electrónico")

    response = client.post(URL, json=_registration())

    assert response.status_code == 409
    assert PatientRepository(db_session).find_by_email("maria.gomez@correo.com") is None


def test_staff_cannot_read_patient_profile(client, login_as):
    login_as(Role.AGENDADOR)

    assert client.get("/api/v1/patients/me").status_code == 403
