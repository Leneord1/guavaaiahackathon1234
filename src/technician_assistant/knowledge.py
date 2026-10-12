"""Shop-manual extraction and Guava retrieval."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from .paths import MANUALS_DIR, ensure_data_dirs

logger = logging.getLogger(__name__)


def extract_manual(path: Path) -> str:
    """Extract supported manual text."""
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"Unsupported manual type: {path.suffix}")


class ManualKnowledge:
    """Index user-supplied manuals with Guava DocumentQA."""

    def __init__(self, directory: Path = MANUALS_DIR) -> None:
        self.directory = directory
        self.source_names: list[str] = []
        self._qa: Any | None = None

    def refresh(self) -> list[str]:
        """Load manuals and rebuild Guava index."""
        ensure_data_dirs()
        self.directory.mkdir(parents=True, exist_ok=True)
        paths = sorted(
            path
            for path in self.directory.iterdir()
            if path.is_file() and path.suffix.lower() in {".pdf", ".txt"}
        )
        documents: list[str] = []
        ids: list[str] = []
        for path in paths:
            try:
                text = extract_manual(path).strip()
            except Exception as exc:
                logger.warning("Could not read manual %s: %s", path.name, exc)
                continue
            if text:
                documents.append(f"SOURCE: {path.name}\n\n{text}")
                ids.append(path.name)
        self.source_names = ids
        if not documents:
            self._qa = None
            return []
        from guava.helpers.rag import DocumentQA

        self._qa = DocumentQA(
            documents=documents,
            ids=ids,
            namespace="technician-shop-manuals",
            instructions=(
                "Answer only from supplied shop manuals. Cite source filenames. "
                "State when evidence is absent. Never invent specifications."
            ),
        )
        return self.source_names.copy()

    def answer(self, question: str) -> str:
        """Answer with manuals or explicit fallback."""
        if self._qa is None:
            return (
                "No matching shop manual is loaded. Apply general diagnostic reasoning only, "
                "verify specifications in approved service information, and state this limitation."
            )
        return str(self._qa.ask(question))
