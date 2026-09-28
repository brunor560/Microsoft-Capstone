"""Phase 5: weighted scoring harness (project brief, section 6).

Final score = 0.35F + 0.25S + 0.20Q + 0.10T + 0.10H

  F -- Functionality
       Percentage of acceptance tests passed.

  S -- Security
       100 when all required security checks complete successfully and find
       no leaks.
       0 when a leak is detected OR when security cannot be verified.

       These two zero-score cases are distinguished by GraderResult.error:
           leak detected       -> score 0, no grader error
           scanner/check fails -> score 0, grader error, unreliable scorecard

  Q -- Code Quality
       Quality criteria compared with the pre-agent baseline where possible.

  T -- Token Efficiency
       Derived from measured model token usage.

  H -- Collaboration
       Derived from recorded human interventions.

F, S and Q are measured by sandbox graders. T and H are computed from
host-side telemetry and intervention records.

A final numeric score may still be produced when a grader fails, but the
scorecard is marked unreliable through `grader_errors`. Consumers should
never treat an unreliable scorecard as a valid benchmark result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

WEIGHTS: dict[str, float] = {
    "functionality": 0.35,
    "security": 0.25,
    "quality": 0.20,
    "token_efficiency": 0.10,
    "collaboration": 0.10,
}


class ScoringError(RuntimeError):
    """Raised when a score cannot be computed from the inputs given."""


@dataclass
class Scorecard:
    """The five dimensions and their weighted combination."""

    functionality: float
    security: float
    quality: float
    token_efficiency: float
    collaboration: float
    evidence: dict[str, Any] = field(default_factory=dict)
    grader_errors: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        for name in WEIGHTS:
            value = getattr(self, name)
            if not 0.0 <= value <= 100.0:
                raise ScoringError(
                    f"{name} must be within 0-100, got {value}"
                )

    @property
    def dimensions(self) -> dict[str, float]:
        return {name: getattr(self, name) for name in WEIGHTS}

    @property
    def final_score(self) -> float:
        return sum(WEIGHTS[name] * value for name, value in self.dimensions.items())

    @property
    def reliable(self) -> bool:
        """False when any grader failed to run.

        A crashed grader yields 0 for its dimension, which is
        indistinguishable from a genuine 0 unless it is flagged. Consumers
        should treat an unreliable scorecard as provisional.
        """
        return not self.grader_errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "final_score": round(self.final_score, 2),
            "reliable": self.reliable,
            "weights": dict(WEIGHTS),
            "dimensions": {k: round(v, 2) for k, v in self.dimensions.items()},
            "weighted_contributions": {
                k: round(WEIGHTS[k] * v, 2) for k, v in self.dimensions.items()
            },
            "grader_errors": list(self.grader_errors),
            "evidence": self.evidence,
        }


def build_scorecard(
    *,
    functionality,
    security,
    quality,
    telemetry,
    interventions,
    max_tokens: int,
) -> Scorecard:
    """Assemble a Scorecard from grader results and host-side telemetry.

    `functionality`, `security` and `quality` are GraderResult objects;
    `telemetry` is a RunTelemetry; `interventions` is an InterventionLog.
    """
    grader_results = {
        "functionality": functionality,
        "security": security,
        "quality": quality,
    }

    errors = [
        f"{name}: {result.error}"
        for name, result in grader_results.items()
        if getattr(result, "failed", False)
    ]

    return Scorecard(
        functionality=functionality.score,
        security=security.score,
        quality=quality.score,
        token_efficiency=telemetry.token_efficiency(max_tokens),
        collaboration=float(interventions.collaboration_score),
        grader_errors=errors,
        evidence={
            name: result.to_dict() for name, result in grader_results.items()
        }
        | {
            "token_efficiency": {
                "total_tokens": telemetry.total_tokens,
                "max_tokens": max_tokens,
            },
            "collaboration": {
                "consultations": interventions.total_inputs,
                "interventions": interventions.interventions,
            },
        },
    )
