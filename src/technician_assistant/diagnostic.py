"""Automotive diagnostic sanity-check workflow."""

from __future__ import annotations

from typing import Any

import guava

INTAKE_FIELDS = (
    ("vehicle", "Vehicle year, make, model, engine, mileage, and relevant configuration."),
    ("complaint", "Customer complaint and exact operating conditions."),
    ("codes_data", "Diagnostic trouble codes, scan data, freeze-frame data, and warning lamps."),
    ("tests_results", "Tests already performed, measured values, specifications, and results."),
    ("current_hypothesis", "Current failure theory and evidence supporting it."),
)

REVIEW_FIELDS = (
    (
        "contradictions",
        "Identify conflicting observations or say none. Ask technician to verify each conflict.",
    ),
    (
        "missing_tests",
        "Identify missing low-risk tests needed before parts replacement.",
    ),
    (
        "disconfirming_evidence",
        "Ask what result would disprove the current hypothesis.",
    ),
    (
        "safety_checks",
        "Confirm applicable high-voltage, fuel, lift, rotating equipment, heat, "
        "and restraint safety.",
    ),
    (
        "next_test",
        "Agree on one safest, highest-information next test and expected outcomes.",
    ),
    (
        "confidence",
        "Capture confidence as low, medium, or high and why.",
    ),
)


def start_diagnostic(call: guava.Call) -> None:
    """Start diagnostic intake."""
    call.set_task(
        "diagnostic_intake",
        objective=(
            "Gather facts before offering conclusions. Treat technician as decision-maker. "
            "Do not recommend replacing parts without a confirming test."
        ),
        checklist=[
            guava.Field(key=key, field_type="text", description=description)
            for key, description in INTAKE_FIELDS
        ],
    )


def intake_query(call: guava.Call) -> str:
    """Build grounded manual query."""
    values = {key: call.get_field(key) for key, _ in INTAKE_FIELDS}
    return (
        "Find applicable diagnostic procedures, specifications, warnings, prerequisites, "
        f"and likely next tests for this case: {values}"
    )


def start_review(call: guava.Call, manual_context: str) -> None:
    """Start reasoning review with manual context."""
    call.add_info(
        "shop_manual_context",
        {
            "content": manual_context,
            "instruction": (
                "Distinguish cited manual facts from general reasoning. Never invent values. "
                "Stop and recommend approved service information for unsupported "
                "safety-critical work."
            ),
        },
    )
    call.set_task(
        "diagnostic_review",
        objective=(
            "Sanity-check reasoning aloud. Highlight contradictions, missing evidence, "
            "unsafe steps, and confirmation bias. End with one next test, not a "
            "definitive repair authorization."
        ),
        checklist=[
            guava.Field(key=key, field_type="text", description=description)
            for key, description in REVIEW_FIELDS
        ],
    )


def diagnostic_report(call: guava.Call, manual_context: str) -> dict[str, Any]:
    """Collect complete diagnostic report."""
    report = {key: call.get_field(key) for key, _ in INTAKE_FIELDS + REVIEW_FIELDS}
    report["manual_context"] = manual_context
    report["disclaimer"] = (
        "Decision support only. Verify procedures and specifications in approved "
        "service information."
    )
    return report
