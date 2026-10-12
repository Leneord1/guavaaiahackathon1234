"""Guava configuration page."""

from PySide6.QtCore import QSettings, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..credentials import CredentialService


class GuavaSetupPage(QWidget):
    """Collect protected Guava configuration."""

    configuration_changed = Signal()

    def __init__(self, credentials: CredentialService) -> None:
        super().__init__()
        self.credentials = credentials
        self.settings = QSettings("GuavaHackathon", "TechnicianVoiceAssistant")
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("gva-...")
        self.webrtc_code = QLineEdit(str(self.settings.value("webrtc_code", "")))
        self.webrtc_code.setPlaceholderText("Optional grtc-...")
        self.status = QLabel()

        save_button = QPushButton("Save Guava settings")
        remove_button = QPushButton("Remove API key")
        save_button.clicked.connect(self.save)
        remove_button.clicked.connect(self.remove)

        form = QFormLayout()
        form.addRow("Guava API key", self.api_key)
        form.addRow("WebRTC code", self.webrtc_code)
        actions = QHBoxLayout()
        actions.addWidget(save_button)
        actions.addWidget(remove_button)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Guava setup</h2>"))
        layout.addWidget(
            QLabel(
                "API key is protected by Windows Credential Manager. "
                "Connectivity is confirmed when agent reaches running state."
            )
        )
        layout.addLayout(form)
        layout.addLayout(actions)
        layout.addWidget(self.status)
        layout.addStretch()
        self._refresh_status()

    def save(self) -> None:
        """Save protected configuration."""
        try:
            if self.api_key.text().strip():
                self.credentials.save_guava_key(self.api_key.text())
                self.api_key.clear()
            code = self.webrtc_code.text().strip()
            if code and not code.startswith("grtc-"):
                raise ValueError("WebRTC code must start with grtc-.")
            self.settings.setValue("webrtc_code", code)
            self.status.setText("Settings saved.")
            self.configuration_changed.emit()
        except Exception as exc:
            self.status.setText(str(exc))
        self._refresh_status()

    def remove(self) -> None:
        """Delete protected Guava key."""
        self.credentials.delete_guava_key()
        self.status.setText("API key removed.")
        self.configuration_changed.emit()

    def current_webrtc_code(self) -> str:
        """Return optional WebRTC code."""
        return str(self.settings.value("webrtc_code", "")).strip()

    def _refresh_status(self) -> None:
        """Show key presence without revealing it."""
        if self.credentials.get_guava_key():
            self.status.setText("Guava API key configured.")
