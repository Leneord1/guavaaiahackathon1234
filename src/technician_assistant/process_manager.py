"""Managed Guava worker process."""

from __future__ import annotations

import re
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, Signal

from .credentials import CredentialService


class GuavaProcessManager(QObject):
    """Start and monitor `guava run ./my-agent`."""

    status_changed = Signal(str)
    log_received = Signal(str)

    def __init__(
        self,
        credentials: CredentialService,
        project_root: Path | None = None,
    ) -> None:
        super().__init__()
        self.credentials = credentials
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.started.connect(lambda: self.status_changed.emit("running"))
        self.process.finished.connect(lambda *_: self.status_changed.emit("stopped"))
        self.process.errorOccurred.connect(lambda *_: self.status_changed.emit("error"))

    def start(self, webrtc_code: str = "") -> None:
        """Start one worker instance."""
        if self.process.state() != QProcess.ProcessState.NotRunning:
            return
        api_key = self.credentials.get_guava_key()
        if not api_key:
            raise ValueError("Add a Guava API key before starting the agent.")
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("GUAVA_API_KEY", api_key)
        environment.insert("GUAVA_AGENT_NUMBER", "+12402122724")
        if webrtc_code:
            environment.insert("GUAVA_WEBRTC_CODE", webrtc_code)
        self.process.setProcessEnvironment(environment)
        self.process.setWorkingDirectory(str(self.project_root))
        self.status_changed.emit("starting")
        self.process.start("guava", ["run", "./my-agent"])

    def stop(self) -> None:
        """Stop worker cleanly."""
        if self.process.state() == QProcess.ProcessState.NotRunning:
            return
        self.process.terminate()
        if not self.process.waitForFinished(5000):
            self.process.kill()
            self.process.waitForFinished(2000)

    def restart(self, webrtc_code: str = "") -> None:
        """Restart worker."""
        self.stop()
        self.start(webrtc_code)

    def _read_output(self) -> None:
        """Read and redact worker logs."""
        output = bytes(self.process.readAllStandardOutput().data()).decode(errors="replace")
        api_key = self.credentials.get_guava_key()
        if api_key:
            output = output.replace(api_key, "[REDACTED]")
        output = re.sub(r"\bgva-[A-Za-z0-9._-]+", "[REDACTED]", output)
        if "Started listing on phone number" in output:
            self.status_changed.emit("ready")
        self.log_received.emit(output.rstrip())
