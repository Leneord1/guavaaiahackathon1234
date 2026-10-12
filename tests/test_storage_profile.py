"""Persistence and runtime-state tests."""

from pathlib import Path

import pytest

from technician_assistant.profile import ProfileService
from technician_assistant.storage import Storage


def test_report_round_trip(tmp_path: Path) -> None:
    """Save and retrieve structured report."""
    storage = Storage(tmp_path / "assistant.db")
    report_id = storage.save_report(
        "call-1",
        "diagnostic_check",
        {"next_test": "Voltage drop test"},
        ["manual.pdf"],
    )

    report = storage.list_reports()[0]

    assert report.id == report_id
    assert report.call_id == "call-1"
    assert report.payload == {"next_test": "Voltage drop test"}
    assert report.sources == ["manual.pdf"]


def test_dynamic_profile_field_replaces_previous_value(tmp_path: Path) -> None:
    """Maintain exactly one runtime field."""
    service = ProfileService(Storage(tmp_path / "assistant.db"))
    service.save("Certification", "text", "ASE A6")
    service.save("Bay", "number", "4")

    field = service.load()

    assert field is not None
    assert field.label == "Bay"
    assert field.value == "4"
    assert field.as_context()["field_value"] == "4"


def test_dynamic_profile_rejects_invalid_boolean(tmp_path: Path) -> None:
    """Reject malformed runtime values."""
    service = ProfileService(Storage(tmp_path / "assistant.db"))

    with pytest.raises(ValueError, match="Boolean"):
        service.save("Hybrid certified", "boolean", "sometimes")
