"""Shop-manual grounding tests."""

from pathlib import Path
from typing import Any

import pytest

from technician_assistant.knowledge import ManualKnowledge, extract_manual


class FakeDocumentQA:
    """Capture indexed documents."""

    created: "FakeDocumentQA | None" = None

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        FakeDocumentQA.created = self

    def ask(self, question: str) -> str:
        """Return grounded fake answer."""
        return f"SOURCE: service.txt — answer for {question}"


def test_extracts_text_manual(tmp_path: Path) -> None:
    """Read UTF-8 text manuals."""
    manual = tmp_path / "service.txt"
    manual.write_text("Connector C101 pin 2.", encoding="utf-8")

    assert extract_manual(manual) == "Connector C101 pin 2."


def test_indexes_manual_with_stable_source(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Pass source label and stable ID into Guava DocumentQA."""
    manual = tmp_path / "service.txt"
    manual.write_text("Specification: 12 volts.", encoding="utf-8")
    monkeypatch.setattr("guava.helpers.rag.DocumentQA", FakeDocumentQA)
    knowledge = ManualKnowledge(tmp_path)

    sources = knowledge.refresh()

    assert sources == ["service.txt"]
    assert FakeDocumentQA.created is not None
    assert FakeDocumentQA.created.kwargs["ids"] == ["service.txt"]
    assert "SOURCE: service.txt" in FakeDocumentQA.created.kwargs["documents"][0]
    assert "SOURCE: service.txt" in knowledge.answer("What is the voltage?")


def test_explicit_fallback_without_manuals(tmp_path: Path) -> None:
    """Disclose missing manual evidence."""
    knowledge = ManualKnowledge(tmp_path)
    knowledge.refresh()

    assert "No matching shop manual" in knowledge.answer("Any question")
