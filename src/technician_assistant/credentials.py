"""Windows-protected application credentials."""

from __future__ import annotations

import keyring

from .storage import Storage

SERVICE_NAME = "TechnicianVoiceAssistant"
GUAVA_ACCOUNT = "guava-api-key"


class CredentialService:
    """Store secrets through system credential backend."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def save_guava_key(self, api_key: str) -> None:
        """Validate and protect Guava key."""
        api_key = api_key.strip()
        if not api_key.startswith("gva-") or len(api_key) < 12:
            raise ValueError("Guava API key must start with gva-.")
        keyring.set_password(SERVICE_NAME, GUAVA_ACCOUNT, api_key)

    def get_guava_key(self) -> str | None:
        """Read protected Guava key."""
        return keyring.get_password(SERVICE_NAME, GUAVA_ACCOUNT)

    def delete_guava_key(self) -> None:
        """Remove protected Guava key."""
        try:
            keyring.delete_password(SERVICE_NAME, GUAVA_ACCOUNT)
        except keyring.errors.PasswordDeleteError:
            pass

    def save_provider(self, provider_id: str, username: str, password: str) -> None:
        """Protect one provider account."""
        username = username.strip()
        if not provider_id or not username or not password:
            raise ValueError("Provider, username, and password are required.")
        keyring.set_password(SERVICE_NAME, f"provider:{provider_id}", password)
        self.storage.save_provider_username(provider_id, username)

    def provider_password(self, provider_id: str) -> str | None:
        """Read provider password for future approved adapters."""
        return keyring.get_password(SERVICE_NAME, f"provider:{provider_id}")

    def delete_provider(self, provider_id: str) -> None:
        """Remove provider account."""
        try:
            keyring.delete_password(SERVICE_NAME, f"provider:{provider_id}")
        except keyring.errors.PasswordDeleteError:
            pass
        self.storage.delete_provider_username(provider_id)
