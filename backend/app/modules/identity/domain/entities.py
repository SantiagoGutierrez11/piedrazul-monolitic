"""Entidades del módulo de identidad."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TokenSet:
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int


@dataclass(frozen=True)
class NewUser:
    email: str
    password: str
    first_name: str
    last_name: str
