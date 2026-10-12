"""Guava agent composition."""

from __future__ import annotations

import logging
import threading
from typing import Any

import guava
from guava.events import BotSessionEnded

from .diagnostic import diagnostic_report, intake_query, start_diagnostic, start_review
from .interview import interview_report, start_interview
from .knowledge import ManualKnowledge
from .profile import ProfileService
from .storage import Storage

logger = logging.getLogger(__name__)


def create_agent(
    storage: Storage | None = None,
    knowledge: ManualKnowledge | None = None,
) -> guava.Agent:
    """Create configured technician agent."""
    store = storage or Storage()
    profile = ProfileService(store)
    manuals = knowledge or ManualKnowledge()
    try:
        manuals.refresh()
    except Exception as exc:
        logger.warning("Manual index unavailable: %s", exc)

    states: dict[str, dict[str, Any]] = {}
    state_lock = threading.Lock()
    agent = guava.Agent(
        name="TorqueCheck",
        organization="Technician Voice Assistant",
        purpose=(
            "Interview automotive technicians or sanity-check diagnostic reasoning "
            "using supplied shop manuals."
        ),
    )

    @agent.on_call_start
    def on_call_start(call: guava.Call) -> None:
        """Route caller into one workflow."""
        with state_lock:
            states[call.id] = {}
        dynamic_field = profile.load()
        if dynamic_field:
            call.add_info("user_profile", dynamic_field.as_context())
        call.set_task(
            "select_mode",
            objective=(
                "Welcome the caller, disclose that this is an AI voice assistant, "
                "then determine which workflow they want."
            ),
            checklist=[
                guava.Field(
                    key="mode",
                    field_type="multiple_choice",
                    choices=["research_interview", "diagnostic_check"],
                    description=(
                        "Ask whether they want the technician research interview "
                        "or a diagnostic sanity check."
                    ),
                )
            ],
        )

    @agent.on_task_complete("select_mode")
    def on_mode_selected(call: guava.Call) -> None:
        """Start selected workflow."""
        mode = str(call.get_field("mode"))
        with state_lock:
            states.setdefault(call.id, {})["mode"] = mode
        if mode == "research_interview":
            start_interview(call)
        else:
            start_diagnostic(call)

    @agent.on_task_complete("research_interview")
    def on_interview_complete(call: guava.Call) -> None:
        """Save interview report."""
        payload = interview_report(call)
        store.save_report(call.id, "research_interview", payload)
        call.hangup(
            "Thank the technician for their time. Confirm their feedback was saved, "
            "then end the call."
        )

    @agent.on_task_complete("diagnostic_intake")
    def on_diagnostic_intake(call: guava.Call) -> None:
        """Ground review in shop manuals."""
        context = manuals.answer(intake_query(call))
        with state_lock:
            states.setdefault(call.id, {})["manual_context"] = context
        start_review(call, context)

    @agent.on_task_complete("diagnostic_review")
    def on_diagnostic_review(call: guava.Call) -> None:
        """Save diagnostic report."""
        with state_lock:
            context = str(states.get(call.id, {}).get("manual_context", ""))
        payload = diagnostic_report(call, context)
        store.save_report(call.id, "diagnostic_check", payload, manuals.source_names)
        call.hangup(
            "Recap the next test, confidence, and safety limits. Remind the technician "
            "to verify approved service information, then end the call."
        )

    @agent.on_question
    def on_question(call: guava.Call, question: str) -> str:
        """Answer diagnostic questions from supplied manuals."""
        with state_lock:
            mode = states.get(call.id, {}).get("mode")
        if mode == "diagnostic_check":
            return manuals.answer(question)
        return (
            "I am here to learn from your experience during this interview. "
            "I can clarify a question, but I will not pitch or lead your answer."
        )

    @agent.on_session_end
    def on_session_end(call: guava.Call, event: BotSessionEnded) -> None:
        """Release per-call state."""
        with state_lock:
            states.pop(call.id, None)
        logger.info("Session ended: %s (%s)", call.id, event.termination_reason)

    return agent
