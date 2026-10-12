"""Technician discovery interview workflow."""

from __future__ import annotations

from typing import Any

import guava

INTERVIEW_FIELDS = (
    (
        "stuck_diagnosis",
        "Walk through the last diagnosis where they got stuck, including vehicle and complaint.",
    ),
    (
        "first_resource",
        "Ask what they did first: ask someone, search online, use ALLDATA, Identifix, "
        "ProDemand, or keep testing, and why.",
    ),
    (
        "time_to_confidence",
        "Ask how long it took to get from stuck to confident and how much time was paid.",
    ),
    (
        "master_tech_goal",
        "Ask whether they seek an answer, confirmation, or the next test from a master tech.",
    ),
    (
        "comeback_story",
        "Ask about a gut call that caused a comeback or wrong part and what could have caught it.",
    ),
    (
        "trust_concerns",
        "Ask what they trust least about forums, YouTube, or ChatGPT for diagnosis.",
    ),
    (
        "lookup_workflow",
        "Ask how they look up information under the hood and whether they use voice.",
    ),
    (
        "sanity_checker_fit",
        "Ask when a 30-second spoken reasoning double-check helps and when it annoys.",
    ),
    (
        "tool_spending",
        "Ask who pays for information and scan tools and recent out-of-pocket purchases.",
    ),
    (
        "one_improvement",
        "Ask what single diagnostic problem they would fix in their shop.",
    ),
)


def start_interview(call: guava.Call) -> None:
    """Start research interview task."""
    checklist: list[Any] = [
        "Say exactly: I'm not selling anything. I'm trying to learn how techs get "
        "unstuck on tough diagnostics."
    ]
    checklist.extend(
        guava.Field(key=key, field_type="text", description=description)
        for key, description in INTERVIEW_FIELDS
    )
    call.set_task(
        "research_interview",
        objective=(
            "Conduct a natural technician research interview. Ask one concise question at a time, "
            "use brief follow-ups for specifics, and do not pitch a product."
        ),
        checklist=checklist,
    )


def interview_report(call: guava.Call) -> dict[str, Any]:
    """Collect structured interview result."""
    return {key: call.get_field(key) for key, _ in INTERVIEW_FIELDS}
