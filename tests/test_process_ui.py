"""Desktop process and page tests."""

from pathlib import Path
from typing import Any

from PySide6.QtCore import QByteArray, QProcess

from technician_assistant.process_manager import GuavaProcessManager


class FakeCredentials:
    """Provide one test Guava key."""

    def get_guava_key(self) -> str:
        """Return test key."""
        return "gva-test-secret-key"


class FakeProcess:
    """Capture process configuration."""

    def __init__(self) -> None:
        self.environment: Any = None
        self.directory = ""
        self.command = ""
        self.arguments: list[str] = []

    def state(self) -> QProcess.ProcessState:
        """Report stopped process."""
        return QProcess.ProcessState.NotRunning

    def setProcessEnvironment(self, environment: Any) -> None:
        """Capture process environment."""
        self.environment = environment

    def setWorkingDirectory(self, directory: str) -> None:
        """Capture working directory."""
        self.directory = directory

    def start(self, command: str, arguments: list[str]) -> None:
        """Capture command."""
        self.command = command
        self.arguments = arguments

    def readAllStandardOutput(self) -> QByteArray:
        """Return output containing secret."""
        return QByteArray(b"connected with gva-test-secret-key")


def test_process_manager_injects_key_without_command_argument(
    qtbot: Any,
    tmp_path: Path,
) -> None:
    """Inject secret through child environment."""
    manager = GuavaProcessManager(FakeCredentials(), tmp_path)  # type: ignore[arg-type]
    fake = FakeProcess()
    manager.process = fake  # type: ignore[assignment]

    manager.start("grtc-test")

    assert fake.command == "guava"
    assert fake.arguments == ["run", "./my-agent"]
    assert fake.environment.value("GUAVA_API_KEY") == "gva-test-secret-key"
    assert "gva-test-secret-key" not in " ".join(fake.arguments)


def test_process_logs_are_redacted(qtbot: Any, tmp_path: Path) -> None:
    """Remove Guava key from displayed logs."""
    manager = GuavaProcessManager(FakeCredentials(), tmp_path)  # type: ignore[arg-type]
    manager.process = FakeProcess()  # type: ignore[assignment]
    received: list[str] = []
    manager.log_received.connect(received.append)

    manager._read_output()

    assert received == ["connected with [REDACTED]"]
