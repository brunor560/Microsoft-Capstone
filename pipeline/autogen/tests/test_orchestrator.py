"""Phase 3 tests for the intervention counter and H score.

Fully offline: no LLM, no Docker. The H dimension is pure arithmetic over
recorded operator replies, so it is verifiable without a model.
"""

from __future__ import annotations

import pytest

from harness.orchestrator import InterventionLog, make_logging_input_func


# --- H score arithmetic ------------------------------------------------------


def test_perfect_collaboration_scores_100():
    """No operator input at all means a fully autonomous run."""
    assert InterventionLog().collaboration_score == 100


def test_bare_approvals_are_not_interventions():
    """Pressing Enter is assent, not correction -- H must stay at 100."""
    log = InterventionLog()
    for reply in ("", "y", "yes", "ok", "approve", "continue", "c"):
        log.record("prompt> ", reply)

    assert log.total_inputs == 7
    assert log.interventions == 0
    assert log.collaboration_score == 100


def test_approval_matching_is_case_and_space_insensitive():
    log = InterventionLog()
    log.record("p> ", "  YES  ")
    log.record("p> ", "Ok")
    assert log.interventions == 0


def test_each_substantive_reply_costs_10_points():
    log = InterventionLog()
    log.record("p> ", "no, use pytest instead")
    assert log.collaboration_score == 90

    log.record("p> ", "you deleted the wrong file")
    assert log.collaboration_score == 80


def test_h_score_is_floored_at_zero():
    """11 interventions must not produce a negative score."""
    log = InterventionLog()
    for i in range(11):
        log.record("p> ", f"correction {i}")

    assert log.interventions == 11
    assert log.collaboration_score == 0


def test_mixed_approvals_and_corrections():
    log = InterventionLog()
    log.record("p> ", "")                       # approval
    log.record("p> ", "fix the import")          # intervention
    log.record("p> ", "y")                      # approval
    log.record("p> ", "wrong directory")         # intervention

    assert log.total_inputs == 4
    assert log.interventions == 2
    assert log.collaboration_score == 80


# --- the input callback ------------------------------------------------------


async def test_scripted_input_records_replies():
    log = InterventionLog()
    func = make_logging_input_func(log, scripted=["first", "second"])

    assert await func("prompt A> ") == "first"
    assert await func("prompt B> ") == "second"

    assert log.prompts == ["prompt A> ", "prompt B> "]
    assert log.replies == ["first", "second"]
    assert log.interventions == 2


async def test_exhausted_script_terminates_instead_of_hanging():
    """A test must never block forever waiting on stdin."""
    log = InterventionLog()
    func = make_logging_input_func(log, scripted=[])

    assert await func("prompt> ") == "TERMINATE"


async def test_scripted_approvals_do_not_reduce_h():
    log = InterventionLog()
    func = make_logging_input_func(log, scripted=["", "y"])

    await func("p> ")
    await func("p> ")

    assert log.total_inputs == 2
    assert log.collaboration_score == 100


# --- termination wiring ------------------------------------------------------


class _StubClient:
    """Minimal ChatCompletionClient stand-in for wiring assertions.

    Never called: these tests only inspect how the team was assembled.
    """

    def __init__(self):
        self.model_info = {
            "family": "unknown",
            "function_calling": True,
            "json_output": False,
            "vision": False,
            "structured_output": False,
        }


def test_termination_does_not_fire_on_the_task_prompt():
    """Regression: the TERMINATE sentinel must be scoped to the coder.

    A bare TextMentionTermination also inspects the incoming user task, so a
    task containing the word "TERMINATE" -- e.g. 'reply TERMINATE when done'
    -- ended the run before any model call occurred. The live Phase 3 gate
    caught this as a 1-message run with zero operator consultations.
    """
    from autogen_agentchat.messages import TextMessage
    from harness.orchestrator import build_orchestration
    from harness.model_profiles import Limits

    orchestration = build_orchestration(
        _StubClient(),
        limits=Limits(max_consecutive_auto_replies=5, max_total_tokens=15000),
        code_executor=None,
        scripted_input=[""],
    )

    condition = orchestration.team._termination_condition
    user_task = TextMessage(
        content="Do the work, then reply TERMINATE.", source="user"
    )

    # The user's own message must NOT satisfy the termination condition.
    import asyncio

    assert asyncio.run(condition([user_task])) is None


def test_termination_fires_when_the_coder_says_terminate():
    from autogen_agentchat.messages import TextMessage
    from harness.orchestrator import build_orchestration
    from harness.model_profiles import Limits

    orchestration = build_orchestration(
        _StubClient(),
        limits=Limits(max_consecutive_auto_replies=5, max_total_tokens=15000),
        code_executor=None,
        scripted_input=[""],
    )

    condition = orchestration.team._termination_condition
    coder_done = TextMessage(content="All tests pass. TERMINATE", source="coder")

    import asyncio

    assert asyncio.run(condition([coder_done])) is not None


def test_message_ceiling_derives_from_limits():
    """5 coder replies == 10 messages with two alternating participants."""
    from harness.orchestrator import build_orchestration
    from harness.model_profiles import Limits

    orchestration = build_orchestration(
        _StubClient(),
        limits=Limits(max_consecutive_auto_replies=5, max_total_tokens=15000),
        code_executor=None,
        scripted_input=[""],
    )

    assert orchestration.limits.max_consecutive_auto_replies == 5
    assert orchestration.limits.max_total_tokens == 15000
