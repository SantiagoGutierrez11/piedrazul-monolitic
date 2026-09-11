"""Pruebas de la configuración del sistema (ventana de agendamiento y horarios por profesional)."""


def test_global_configuration_returns_default_when_empty(client):
    response = client.get("/api/v1/configuration/global")

    assert response.status_code == 200
    assert response.json() == {"weeks": 4}


def test_update_appointment_window_persists_value(client):
    client.put("/api/v1/configuration/global/appointment-window", json={"weeks": 8})

    assert client.get("/api/v1/configuration/global").json() == {"weeks": 8}


def test_update_appointment_window_rejects_out_of_range(client):
    response = client.put("/api/v1/configuration/global/appointment-window", json={"weeks": 60})

    assert response.status_code == 400
    assert "entre 1 y 52" in response.json()["message"]


def test_doctor_schedule_is_replaced_on_update(client):
    payload = {
        "schedules": [
            {"dayOfWeek": 1, "startTime": "08:00:00", "endTime": "12:00:00", "intervalMinutes": 30},
            {"dayOfWeek": 2, "startTime": "14:00:00", "endTime": "18:00:00", "intervalMinutes": 20},
        ]
    }
    response = client.put("/api/v1/configuration/doctor/1/schedule", json=payload)

    assert response.status_code == 200
    assert client.get("/api/v1/configuration/doctor/1/schedule").json() == payload["schedules"]


def test_doctor_schedule_rejects_inverted_hours(client):
    payload = {
        "schedules": [
            {"dayOfWeek": 1, "startTime": "18:00:00", "endTime": "08:00:00", "intervalMinutes": 30}
        ]
    }
    response = client.put("/api/v1/configuration/doctor/1/schedule", json=payload)

    assert response.status_code == 400
    assert "anterior a la hora de fin" in response.json()["message"]


def test_doctor_schedule_rejects_duplicated_day(client):
    payload = {
        "schedules": [
            {"dayOfWeek": 1, "startTime": "08:00:00", "endTime": "12:00:00", "intervalMinutes": 30},
            {"dayOfWeek": 1, "startTime": "14:00:00", "endTime": "18:00:00", "intervalMinutes": 30},
        ]
    }
    response = client.put("/api/v1/configuration/doctor/1/schedule", json=payload)

    assert response.status_code == 400
