"""
Bus de eventos in-process.

Reemplaza a RabbitMQ entre microservicios: en el monolito modular, cuando
`configuration` cambia el horario de un médico o la ventana de agendamiento,
publica un evento aquí y los módulos interesados (p. ej. `medical_staff`,
`appointment`) se suscriben, sin acoplarse por import directo ni por red.
"""
from collections import defaultdict
from typing import Callable

_subscribers: dict[str, list[Callable]] = defaultdict(list)


def subscribe(event_name: str, handler: Callable) -> None:
    _subscribers[event_name].append(handler)


def publish(event_name: str, payload: dict) -> None:
    for handler in _subscribers[event_name]:
        handler(payload)
