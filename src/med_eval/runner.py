from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .models import BenchmarkReport, EvaluationCase
from .scoring import score_response


def load_cases(path: str | Path) -> list[EvaluationCase]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [EvaluationCase.model_validate(item) for item in payload]


def run_benchmark(cases, adapter) -> BenchmarkReport:
    scores = []
    valid_outputs = 0

    for case in cases:
        try:
            response = adapter.generate(case)
            score = score_response(case, response)
            valid_outputs += 1
        except ValidationError:
            from .models import CaseScore
            score = CaseScore(
                case_id=case.id,
                concept_coverage=0.0,
                forbidden_claims_found=[],
                safety_flags=["invalid_structured_output"],
                escalation_present=False if case.requires_escalation else None,
                structured_output_valid=False,
            )
        scores.append(score)

    n = max(len(scores), 1)
    return BenchmarkReport(
        cases=len(scores),
        mean_concept_coverage=round(sum(s.concept_coverage for s in scores) / n, 4),
        forbidden_claim_rate=round(sum(bool(s.forbidden_claims_found) for s in scores) / n, 4),
        safety_flag_rate=round(sum(bool(s.safety_flags) for s in scores) / n, 4),
        structured_output_validity=round(valid_outputs / n, 4),
        case_scores=scores,
    )
