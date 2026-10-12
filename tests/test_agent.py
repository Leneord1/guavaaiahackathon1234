"""Registered Guava handler tests."""

from pathlib import Path

from guava.commands import SetTaskCommand
from guava.testing import MockCall

from technician_assistant.agent import create_agent
from technician_assistant.interview import INTERVIEW_FIELDS
from technician_assistant.storage import Storage


class FakeKnowledge:
    """Provide deterministic manual grounding."""

    source_names = ["manual.pdf"]

    def refresh(self) -> list[str]:
        """Return fake source."""
        return self.source_names

    def answer(self, question: str) -> str:
        """Return fake grounded response."""
        return f"SOURCE: manual.pdf — {question}"


def test_registered_interview_route_saves_report(tmp_path: Path) -> None:
    """Route and complete interview through registered handlers."""
    storage = Storage(tmp_path / "assistant.db")
    agent = create_agent(storage, FakeKnowledge())  # type: ignore[arg-type]
    call = MockCall("call-interview")

    assert agent._on_call_start is not None
    agent._on_call_start(call)
    selection = call._command_queue[-1]
    assert isinstance(selection, SetTaskCommand)
    assert selection.task_id == "select_mode"

    call.set_field("mode", "research_interview")
    agent._on_task_complete_handlers["select_mode"](call)
    interview = call._command_queue[-1]
    assert isinstance(interview, SetTaskCommand)
    assert interview.task_id == "research_interview"

    for key, _ in INTERVIEW_FIELDS:
        call.set_field(key, f"value:{key}")
    agent._on_task_complete_handlers["research_interview"](call)

    reports = storage.list_reports()
    assert len(reports) == 1
    assert reports[0].mode == "research_interview"
