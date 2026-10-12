"""Main Windows application window."""

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from ..credentials import CredentialService
from ..process_manager import GuavaProcessManager
from ..profile import ProfileService
from ..storage import Storage
from .guava_setup import GuavaSetupPage
from .pages import HomePage, ManualsPage, ProfilePage, ReportsPage, VoiceAssistantPage
from .provider_accounts import ProviderAccountsPage


class MainWindow(QMainWindow):
    """Host all technician assistant pages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Technician Voice Assistant")
        self.resize(1180, 760)
        storage = Storage()
        credentials = CredentialService(storage)
        profile = ProfileService(storage)
        self.process_manager = GuavaProcessManager(credentials)
        setup = GuavaSetupPage(credentials)

        self.navigation = QListWidget()
        self.navigation.setFixedWidth(210)
        self.stack = QStackedWidget()
        pages = (
            ("Home", HomePage()),
            ("Guava Setup", setup),
            ("Voice Assistant", VoiceAssistantPage(self.process_manager, setup)),
            ("Reports", ReportsPage(storage)),
            ("Manuals", ManualsPage()),
            ("Provider Accounts", ProviderAccountsPage(credentials, storage)),
            ("Profile", ProfilePage(profile)),
        )
        for name, page in pages:
            self.navigation.addItem(name)
            self.stack.addWidget(page)
        self.navigation.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.navigation.setCurrentRow(0)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(self.navigation)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(container)
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #101820; color: #eef4f7; }
            QListWidget { background: #17242d; border: 0; padding: 10px; }
            QListWidget::item { padding: 12px; border-radius: 5px; }
            QListWidget::item:selected { background: #1f8a70; }
            QPushButton { background: #1f8a70; border: 0; padding: 9px 14px; border-radius: 5px; }
            QPushButton:hover { background: #28a987; }
            QLineEdit, QComboBox, QPlainTextEdit {
                background: #f5f7f8; color: #101820; padding: 7px; border-radius: 4px;
            }
            """
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        """Stop managed worker before closing."""
        self.process_manager.stop()
        event.accept()
