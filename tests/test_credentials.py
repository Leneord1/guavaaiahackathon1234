"""Credential protection tests."""

from pathlib import Path

import pytest

from technician_assistant.credentials import CredentialService
from technician_assistant.storage import Storage


def test_guava_key_uses_system_keyring(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Store Guava key outside database."""
    secrets: dict[tuple[str, str], str] = {}
    monkeypatch.setattr(
        "technician_assistant.credentials.keyring.set_password",
        lambda service, account, value: secrets.__setitem__((service, account), value),
    )
    monkeypatch.setattr(
        "technician_assistant.credentials.keyring.get_password",
        lambda service, account: secrets.get((service, account)),
    )
    database = tmp_path / "assistant.db"
    service = CredentialService(Storage(database))

    service.save_guava_key("gva-test-secret-key")

    assert service.get_guava_key() == "gva-test-secret-key"
    assert b"gva-test-secret-key" not in database.read_bytes()


def test_provider_password_uses_keyring(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Persist username without persisting password."""
    secrets: dict[tuple[str, str], str] = {}
    monkeypatch.setattr(
        "technician_assistant.credentials.keyring.set_password",
        lambda service, account, value: secrets.__setitem__((service, account), value),
    )
    service = CredentialService(Storage(tmp_path / "assistant.db"))

    service.save_provider("alldata", "technician@example.com", "private-password")

    assert service.storage.list_provider_usernames()["alldata"] == "technician@example.com"
    assert b"private-password" not in service.storage.path.read_bytes()


def test_rejects_invalid_guava_key(tmp_path: Path) -> None:
    """Reject keys with wrong prefix."""
    service = CredentialService(Storage(tmp_path / "assistant.db"))

    with pytest.raises(ValueError, match="gva-"):
        service.save_guava_key("not-a-guava-key")
