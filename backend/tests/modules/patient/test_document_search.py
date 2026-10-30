"""Formato de la cédula y activación del autocompletado en la búsqueda de pacientes (E7-HU1, 2.1)."""
import pytest

from app.core.exceptions import ValidationError
from app.modules.patient.application.document_search import (
    INVALID_FORMAT,
    TOO_LONG,
    TOO_SHORT,
    full_document,
    suggestion_prefix,
)


def test_suggestions_start_from_the_third_digit():
    assert suggestion_prefix("10") is None
    assert suggestion_prefix("106") == "106"
    assert suggestion_prefix(" 1061234 ") == "1061234"


@pytest.mark.parametrize("text", ["1.061.234.567", "10612a", "106 123", "106-123", "CC1061234567", ""])
def test_only_digits_are_accepted(text):
    with pytest.raises(ValidationError) as error:
        suggestion_prefix(text)
    assert error.value.message == INVALID_FORMAT


def test_an_id_number_has_at_most_ten_digits():
    with pytest.raises(ValidationError) as error:
        suggestion_prefix("10612345678")
    assert error.value.message == TOO_LONG


def test_the_exact_search_needs_the_complete_id_number():
    assert full_document("94512345") == "94512345"
    with pytest.raises(ValidationError) as error:
        full_document("1061")
    assert error.value.message == TOO_SHORT
