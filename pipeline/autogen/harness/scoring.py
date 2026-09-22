"""Phase 5: the weighted scoring harness (project brief, section 6).

Final score = 0.35F + 0.25S + 0.20Q + 0.10T + 0.10H

  F -- Functionality  (pytest pass percentage)
  S -- Security       (binary: any leak => 0)
  Q -- Code Quality   (four sub-criteria vs baseline)
  T -- Token Efficiency (from telemetry)
  H -- Collaboration  (from the intervention log)

T and H are computed on the host from data already captured in Phases 3-4;
F, S and Q come from graders that run inside the sandbox.
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
