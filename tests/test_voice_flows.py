"""Guava voice workflow tests."""

from guava.commands import SetTaskCommand
from guava.testing import MockCall

from technician_assistant.diagnostic import (
    INTAKE_FIELDS,
    REVIEW_FIELDS,
    diagnostic_report,
    intake_query,
    start_diagnostic,
    start_review,
)
from technician_assistant.interview import INTERVIEW_FIELDS, interview_report, start_interview


def test_interview_starts_complete_script() -> None:
    """Create interview task with all discovery fields."""
    call = MockCall("interview-call")

    start_interview(call)

    command = call._command_queue[-1]
    assert isinstance(command, SetTaskCommand)
    assert command.task_id == "research_interview"
    assert len(command.action_items) == len(INTERVIEW_FIELDS) + 1


def test_interview_report_is_structured() -> None:
    """Collect all interview answers."""
    call = MockCall("interview-call")
    for key, _ in INTERVIEW_FIELDS:
        call.set_field(key, f"value:{key}")

    report = interview_report(call)

    assert set(report) == {key for key, _ in INTERVIEW_FIELDS}


def test_diagnostic_intake_and_review() -> None:
    """Build two-stage diagnostic workflow."""
    call = MockCall("diagnostic-call")
    start_diagnostic(call)
    command = call._command_queue[-1]
    assert isinstance(command, SetTaskCommand)
    assert command.task_id == "diagnostic_intake"

    for key, _ in INTAKE_FIELDS:
        call.set_field(key, f"value:{key}")
    assert "value:vehicle" in intake_query(call)

    start_review(call, "SOURCE: manual.pdf")
    review_command = call._command_queue[-1]
    assert isinstance(review_command, SetTaskCommand)
    assert review_command.task_id == "diagnostic_review"


def test_diagnostic_report_includes_safety_and_source_context() -> None:
    """Produce decision-support report."""
    call = MockCall("diagnostic-call")
    for key, _ in INTAKE_FIELDS + REVIEW_FIELDS:
        call.set_field(key, f"value:{key}")

    report = diagnostic_report(call, "SOURCE: manual.pdf")

    assert report["safety_checks"] == "value:safety_checks"
    assert report["manual_context"] == "SOURCE: manual.pdf"
    assert "Decision support only" in report["disclaimer"]
