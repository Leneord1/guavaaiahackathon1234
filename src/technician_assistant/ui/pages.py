"""Primary desktop pages."""

from __future__ import annotations

import json
import shutil
from importlib import import_module
from pathlib import Path
from typing import Any, cast

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..paths import MANUALS_DIR, ensure_data_dirs
from ..process_manager import GuavaProcessManager
from ..profile import SUPPORTED_TYPES, ProfileService
from ..storage import Report, Storage
from .guava_setup import GuavaSetupPage


class HomePage(QWidget):
    """Show hackathon product summary."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h1>Technician Voice Assistant</h1>"))
        layout.addWidget(QLabel("<h2>Call +1 240-212-2724</h2>"))
        layout.addWidget(
            QLabel(
                "Guava AI conducts technician research interviews and sanity-checks "
                "automotive diagnostic reasoning against user-provided shop manuals."
            )
        )
        layout.addWidget(
            QLabel(
                "Decision support only. Always follow approved service information "
                "and applicable safety procedures."
            )
        )
        layout.addStretch()


class VoiceAssistantPage(QWidget):
    """Control Guava worker and optional WebRTC session."""

    def __init__(
        self,
        process_manager: GuavaProcessManager,
        setup_page: GuavaSetupPage,
    ) -> None:
        super().__init__()
        self.process_manager = process_manager
        self.setup_page = setup_page
        self.status = QLabel("stopped")
        self.logs = QPlainTextEdit()
        self.logs.setReadOnly(True)
        self.web: Any = self._create_web_view()
        if self.web:
            self.web.setVisible(False)
        process_manager.status_changed.connect(self.status.setText)
        process_manager.log_received.connect(self.logs.appendPlainText)

        start_button = QPushButton("Start Guava")
        stop_button = QPushButton("Stop Guava")
        restart_button = QPushButton("Restart")
        open_webrtc = QPushButton("Open WebRTC")
        start_button.clicked.connect(self.start)
        stop_button.clicked.connect(process_manager.stop)
        restart_button.clicked.connect(self.restart)
        open_webrtc.clicked.connect(self.open_webrtc)
        actions = QHBoxLayout()
        for button in (start_button, stop_button, restart_button, open_webrtc):
            actions.addWidget(button)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Guava voice agent</h2>"))
        layout.addWidget(QLabel("Required inbound number: +1 240-212-2724"))
        layout.addWidget(self.status)
        layout.addLayout(actions)
        if self.web:
            layout.addWidget(self.web, 2)
        layout.addWidget(self.logs, 1)

    def start(self) -> None:
        """Start Guava worker."""
        try:
            self.process_manager.start(self.setup_page.current_webrtc_code())
        except Exception as exc:
            self.status.setText(str(exc))

    def restart(self) -> None:
        """Restart Guava worker."""
        try:
            self.process_manager.restart(self.setup_page.current_webrtc_code())
        except Exception as exc:
            self.status.setText(str(exc))

    def open_webrtc(self) -> None:
        """Open configured Guava WebRTC client."""
        code = self.setup_page.current_webrtc_code()
        if not code:
            self.status.setText("Add a grtc- WebRTC code in Guava Setup.")
            return
        if self.web:
            self.web.open_code(code)
            self.web.setVisible(True)
            return
        QDesktopServices.openUrl(
            QUrl(f"https://app.goguava.ai/debug-webrtc?webrtc_code={code}")
        )
        self.status.setText(
            "WebRTC opened in default browser. Install webengine extra to embed it."
        )

    def _create_web_view(self) -> QWidget | None:
        """Load optional WebEngine component."""
        try:
            module = import_module("technician_assistant.ui.webrtc_view")
            return cast(QWidget, module.GuavaWebView())
        except ImportError:
            return None


class ReportsPage(QWidget):
    """Browse structured call reports."""

    def __init__(self, storage: Storage) -> None:
        super().__init__()
        self.storage = storage
        self.reports: list[Report] = []
        self.list = QListWidget()
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        self.list.currentRowChanged.connect(self._show_report)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        splitter = QSplitter()
        splitter.addWidget(self.list)
        splitter.addWidget(self.detail)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Call reports</h2>"))
        layout.addWidget(refresh)
        layout.addWidget(splitter)
        self.refresh()

    def refresh(self) -> None:
        """Reload reports."""
        self.reports = self.storage.list_reports()
        self.list.clear()
        for report in self.reports:
            self.list.addItem(f"{report.mode} — {report.created_at}")
        if self.reports:
            self.list.setCurrentRow(0)

    def _show_report(self, index: int) -> None:
        """Render selected report as raw JSON."""
        if index < 0 or index >= len(self.reports):
            self.detail.clear()
            return
        report = self.reports[index]
        self.detail.setPlainText(
            json.dumps(
                {
                    "id": report.id,
                    "call_id": report.call_id,
                    "mode": report.mode,
                    "sources": report.sources,
                    "created_at": report.created_at,
                    "payload": report.payload,
                },
                indent=2,
                ensure_ascii=False,
            )
        )


class ManualsPage(QWidget):
    """Import user-provided shop manuals."""

    def __init__(self) -> None:
        super().__init__()
        ensure_data_dirs()
        self.list = QListWidget()
        self.status = QLabel()
        add = QPushButton("Add PDF or text manual")
        remove = QPushButton("Remove selected")
        add.clicked.connect(self.add_manual)
        remove.clicked.connect(self.remove_manual)
        actions = QHBoxLayout()
        actions.addWidget(add)
        actions.addWidget(remove)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Shop manuals</h2>"))
        layout.addWidget(
            QLabel("Only upload manuals you are authorized to use. Restart Guava after changes.")
        )
        layout.addLayout(actions)
        layout.addWidget(self.list)
        layout.addWidget(self.status)
        self.refresh()

    def refresh(self) -> None:
        """Reload manual list."""
        self.list.clear()
        for path in sorted(MANUALS_DIR.glob("*")):
            if path.suffix.lower() in {".pdf", ".txt"}:
                self.list.addItem(path.name)

    def add_manual(self) -> None:
        """Copy selected manuals into application data."""
        names, _ = QFileDialog.getOpenFileNames(
            self,
            "Add shop manuals",
            "",
            "Manuals (*.pdf *.txt)",
        )
        for name in names:
            source = Path(name)
            shutil.copy2(source, MANUALS_DIR / source.name)
        self.refresh()
        self.status.setText(f"Added {len(names)} manual(s).")

    def remove_manual(self) -> None:
        """Delete selected manual."""
        item = self.list.currentItem()
        if not item:
            return
        (MANUALS_DIR / item.text()).unlink(missing_ok=True)
        self.refresh()


class ProfilePage(QWidget):
    """Edit one dynamic runtime profile field."""

    def __init__(self, service: ProfileService) -> None:
        super().__init__()
        self.service = service
        self.label = QLineEdit()
        self.field_type = QComboBox()
        self.field_type.addItems(SUPPORTED_TYPES)
        self.value = QLineEdit()
        self.status = QLabel()
        save = QPushButton("Save runtime field")
        save.clicked.connect(self.save)
        form = QFormLayout()
        form.addRow("Field label", self.label)
        form.addRow("Type", self.field_type)
        form.addRow("Value", self.value)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Dynamic user state</h2>"))
        layout.addWidget(QLabel("Exactly one profile field is injected into new Guava calls."))
        layout.addLayout(form)
        layout.addWidget(save)
        layout.addWidget(self.status)
        layout.addStretch()
        self.load()

    def load(self) -> None:
        """Load saved runtime field."""
        field = self.service.load()
        if not field:
            return
        self.label.setText(field.label)
        self.field_type.setCurrentText(field.field_type)
        self.value.setText(field.value)

    def save(self) -> None:
        """Validate and save runtime field."""
        try:
            self.service.save(
                self.label.text(),
                self.field_type.currentText(),
                self.value.text(),
            )
            self.status.setText("Runtime field saved.")
        except Exception as exc:
            self.status.setText(str(exc))
