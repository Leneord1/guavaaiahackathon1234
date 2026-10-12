"""Runtime-defined user profile state."""

from __future__ import annotations

from dataclasses import dataclass

from .storage import Storage

SUPPORTED_TYPES = ("text", "number", "boolean")


@dataclass(frozen=True)
class ProfileField:
    label: str
    field_type: str
    value: str

    def as_context(self) -> dict[str, str]:
        """Return safe Guava context."""
        return {
            "field_name": self.label,
            "field_type": self.field_type,
            "field_value": self.value,
        }


class ProfileService:
    """Manage exactly one runtime-defined profile field."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def save(self, label: str, field_type: str, value: str) -> ProfileField:
        """Validate and save current field."""
        label = label.strip()
        value = value.strip()
        if not label:
            raise ValueError("Profile field label is required.")
        if field_type not in SUPPORTED_TYPES:
            raise ValueError("Unsupported profile field type.")
        if field_type == "number":
            float(value)
        if field_type == "boolean" and value.lower() not in {"true", "false"}:
            raise ValueError("Boolean value must be true or false.")
        field = ProfileField(label=label, field_type=field_type, value=value)
        self.storage.save_profile_field(field.label, field.field_type, field.value)
        return field

    def load(self) -> ProfileField | None:
        """Load current field."""
        data = self.storage.get_profile_field()
        return ProfileField(**data) if data else None
