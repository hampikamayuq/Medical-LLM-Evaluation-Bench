from __future__ import annotations

import json
from pathlib import Path

from .models import BenchmarkReport, CaseScore, EvaluationCase
from .scoring import score_response


def load_cases(path: str | Path) -> list[EvaluationCase]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [EvaluationCase.model_validate(item) for item in payload]


def run_benchmark(cases, adapter) -> BenchmarkReport:
    scores: list[CaseScore] = []
    valid_outputs = 0
    errors = 0

    for case in cases:
        try:
            response = adapter.generate(case)
            score = score_response(case, response)
            valid_outputs += 1
        except Exception as exc:
            errors += 1
            score = CaseScore(
                case_id=case.id,
                concept_coverage=0.0,
                forbidden_claims_found=[],
                safety_flags=["adapter_or_output_error"],
                escalation_present=False if case.requires_escalation else None,
                structured_output_valid=False,
                abstained=None,
                error=f"{type(exc).__name__}: {exc}",
            )
        scores.append(score)

    n = max(len(scores), 1)
    valid_abstention_scores = [s for s in scores if s.abstained is not None]
    abstention_denominator = max(len(valid_abstention_scores), 1)

    return BenchmarkReport(
        cases=len(scores),
        mean_concept_coverage=round(sum(s.concept_coverage for s in scores) / n, 4),
        forbidden_claim_rate=round(sum(bool(s.forbidden_claims_found) for s in scores) / n, 4),
        safety_flag_rate=round(sum(bool(s.safety_flags) and s.error is None for s in scores) / n, 4),
        structured_output_validity=round(valid_outputs / n, 4),
        abstention_rate=round(
            sum(bool(s.abstained) for s in valid_abstention_scores) / abstention_denominator, 4
        ),
        error_rate=round(errors / n, 4),
        case_scores=scores,
    )
