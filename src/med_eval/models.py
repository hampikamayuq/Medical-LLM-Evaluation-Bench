from __future__ import annotations

from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    id: str
    task: str
    prompt: str
    expected_concepts: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    requires_escalation: bool = False


class ModelResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    abstained: bool = False


class CaseScore(BaseModel):
    case_id: str
    concept_coverage: float
    forbidden_claims_found: list[str]
    safety_flags: list[str]
    escalation_present: bool | None
    structured_output_valid: bool


class BenchmarkReport(BaseModel):
    cases: int
    mean_concept_coverage: float
    forbidden_claim_rate: float
    safety_flag_rate: float
    structured_output_validity: float
    case_scores: list[CaseScore]
