from __future__ import annotations

from typing import Protocol

from .models import EvaluationCase, ModelResponse


class ModelAdapter(Protocol):
    def generate(self, case: EvaluationCase) -> ModelResponse:
        ...


class MockModelAdapter:
    """Deterministic adapter for local tests and portfolio demonstration."""

    def generate(self, case: EvaluationCase) -> ModelResponse:
        concepts = ", ".join(case.expected_concepts)
        escalation = (
            " Recommend prompt in-person clinical assessment and escalation if red flags are present."
            if case.requires_escalation
            else ""
        )
        answer = f"Key considerations: {concepts}.{escalation}"
        return ModelResponse(answer=answer, confidence=0.78, abstained=False)
