"""Diagnostic provider account page."""

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..credentials import CredentialService
from ..providers import PROVIDERS, provider_by_id
from ..storage import Storage


class ProviderAccountsPage(QWidget):
    """Manage vault-only diagnostic provider accounts."""

    def __init__(self, credentials: CredentialService, storage: Storage) -> None:
        super().__init__()
        self.credentials = credentials
        self.storage = storage
        self.provider = QComboBox()
        for item in PROVIDERS:
            self.provider.addItem(f"{item.category} — {item.name}", item.id)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.status = QLabel()
        self.provider.currentIndexChanged.connect(self._load_username)

        save_button = QPushButton("Save account")
        delete_button = QPushButton("Delete account")
        portal_button = QPushButton("Open official portal")
        save_button.clicked.connect(self.save)
        delete_button.clicked.connect(self.delete)
        portal_button.clicked.connect(self.open_portal)

        form = QFormLayout()
        form.addRow("System", self.provider)
        form.addRow("Username", self.username)
        form.addRow("Password", self.password)
        actions = QHBoxLayout()
        actions.addWidget(save_button)
        actions.addWidget(delete_button)
        actions.addWidget(portal_button)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Diagnostic software accounts</h2>"))
        layout.addWidget(
            QLabel(
                "Vault only. This app does not automate logins or bypass provider access controls."
            )
        )
        layout.addLayout(form)
        layout.addLayout(actions)
        layout.addWidget(self.status)
        layout.addStretch()
        self._load_username()

    def save(self) -> None:
        """Save selected provider account."""
        try:
            provider_id = str(self.provider.currentData())
            self.credentials.save_provider(provider_id, self.username.text(), self.password.text())
            self.password.clear()
            self.status.setText("Account protected.")
        except Exception as exc:
            self.status.setText(str(exc))

    def delete(self) -> None:
        """Delete selected provider account."""
        provider_id = str(self.provider.currentData())
        self.credentials.delete_provider(provider_id)
        self.username.clear()
        self.password.clear()
        self.status.setText("Account removed.")

    def open_portal(self) -> None:
        """Open official provider portal."""
        provider = provider_by_id(str(self.provider.currentData()))
        if not provider.portal_url:
            self.status.setText("Custom provider has no configured portal.")
            return
        QDesktopServices.openUrl(QUrl(provider.portal_url))

    def _load_username(self) -> None:
        """Load non-secret account metadata."""
        usernames = self.storage.list_provider_usernames()
        self.username.setText(usernames.get(str(self.provider.currentData()), ""))
        self.password.clear()
