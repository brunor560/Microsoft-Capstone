"""Phase 5 tests for the weighted scoring harness.

Fully offline: no LLM, no Docker, no API spend. The whole point is that the
score is a pure function of its inputs, so exact values are asserted.
"""

from __future__ import annotations

import pytest

from harness.scoring import WEIGHTS, Scorecard, ScoringError, build_scorecard


def _card(**overrides) -> Scorecard:
    defaults = dict(
        functionality=100.0,
        security=100.0,
        quality=100.0,
        token_efficiency=100.0,
        collaboration=100.0,
    )
    defaults.update(overrides)
    return Scorecard(**defaults)


# --- the weighted formula ----------------------------------------------------


def test_weights_match_the_brief():
    """0.35F + 0.25S + 0.20Q + 0.10T + 0.10H"""
    assert WEIGHTS == {
        "functionality": 0.35,
        "security": 0.25,
        "quality": 0.20,
        "token_efficiency": 0.10,
        "collaboration": 0.10,
    }


def test_weights_sum_to_one():
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)


def test_perfect_run_scores_100():
    assert _card().final_score == pytest.approx(100.0)


def test_zero_run_scores_0():
    card = _card(
        functionality=0.0,
        security=0.0,
        quality=0.0,
        token_efficiency=0.0,
        collaboration=0.0,
    )
    assert card.final_score == pytest.approx(0.0)


def test_worked_example():
    """A hand-computed case, so a weight typo cannot pass silently.

    0.35(80) + 0.25(0) + 0.20(75) + 0.10(50) + 0.10(90)
      = 28 + 0 + 15 + 5 + 9 = 57
    """
    card = _card(
        functionality=80.0,
        security=0.0,
        quality=75.0,
        token_efficiency=50.0,
        collaboration=90.0,
    )
    assert card.final_score == pytest.approx(57.0)


def test_security_zero_caps_the_maximum():
    """A leak costs exactly its 25% weight -- the brief's S=0 short-circuit."""
    assert _card(security=0.0).final_score == pytest.approx(75.0)


def test_each_dimension_contributes_its_weight():
    """Perfect in one dimension only == that dimension's weight x 100."""
    for name, weight in WEIGHTS.items():
        zeros = {k: 0.0 for k in WEIGHTS}
        zeros[name] = 100.0
        assert Scorecard(**zeros).final_score == pytest.approx(weight * 100)


def test_weighted_contributions_sum_to_final_score():
    card = _card(
        functionality=62.0,
        security=100.0,
        quality=41.0,
        token_efficiency=88.0,
        collaboration=70.0,
    )
    payload = card.to_dict()
    assert sum(payload["weighted_contributions"].values()) == pytest.approx(
        payload["final_score"], abs=0.05
    )


# --- input validation --------------------------------------------------------


@pytest.mark.parametrize("bad", [-1.0, 100.1, 150.0])
def test_out_of_range_dimension_is_rejected(bad):
    """Guard against a grader returning a fraction (0-1) instead of 0-100."""
    with pytest.raises(ScoringError, match="must be within 0-100"):
        _card(functionality=bad)


def test_boundary_values_are_accepted():
    assert _card(functionality=0.0).final_score == pytest.approx(65.0)
    assert _card(functionality=100.0).final_score == pytest.approx(100.0)


# --- grader failure vs. a genuine zero ---------------------------------------


def test_scorecard_is_reliable_by_default():
    assert _card().reliable is True


def test_grader_error_marks_the_card_unreliable():
    """A crashed grader must not masquerade as a legitimate zero."""
    card = _card(functionality=0.0, grader_errors=["functionality: no report"])
    assert card.reliable is False
    assert card.to_dict()["reliable"] is False


# --- assembly from real objects ----------------------------------------------


class _Grader:
    def __init__(self, name, score, error=None):
        self.name = name
        self.score = score
        self.error = error

    @property
    def failed(self):
        return self.error is not None

    def to_dict(self):
        return {"name": self.name, "score": self.score, "error": self.error}


class _Telemetry:
    def __init__(self, total_tokens):
        self.total_tokens = total_tokens

    def token_efficiency(self, max_tokens):
        return 100.0 * max(0.0, 1.0 - self.total_tokens / max_tokens)


class _Log:
    def __init__(self, interventions):
        self.interventions = interventions
        self.total_inputs = interventions

    @property
    def collaboration_score(self):
        return max(0, 100 - 10 * self.interventions)


def test_build_scorecard_from_components():
    card = build_scorecard(
        functionality=_Grader("functionality", 80.0),
        security=_Grader("security", 100.0),
        quality=_Grader("quality", 75.0),
        telemetry=_Telemetry(total_tokens=7500),
        interventions=_Log(interventions=2),
        max_tokens=15000,
    )

    assert card.functionality == 80.0
    assert card.token_efficiency == pytest.approx(50.0)
    assert card.collaboration == 80.0
    # 0.35(80) + 0.25(100) + 0.20(75) + 0.10(50) + 0.10(80) = 28+25+15+5+8
    assert card.final_score == pytest.approx(81.0)
    assert card.reliable is True


def test_build_scorecard_propagates_grader_errors():
    card = build_scorecard(
        functionality=_Grader("functionality", 0.0, error="no report produced"),
        security=_Grader("security", 100.0),
        quality=_Grader("quality", 100.0),
        telemetry=_Telemetry(total_tokens=0),
        interventions=_Log(interventions=0),
        max_tokens=15000,
    )

    assert card.reliable is False
    assert "no report produced" in card.grader_errors[0]


def test_evidence_records_all_dimensions():
    card = build_scorecard(
        functionality=_Grader("functionality", 50.0),
        security=_Grader("security", 0.0),
        quality=_Grader("quality", 25.0),
        telemetry=_Telemetry(total_tokens=3000),
        interventions=_Log(interventions=1),
        max_tokens=15000,
    )

    evidence = card.to_dict()["evidence"]
    for key in (
        "functionality",
        "security",
        "quality",
        "token_efficiency",
        "collaboration",
    ):
        assert key in evidence
    assert evidence["collaboration"]["interventions"] == 1
    assert evidence["token_efficiency"]["total_tokens"] == 3000
