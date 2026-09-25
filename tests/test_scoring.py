from med_eval.models import EvaluationCase, ModelResponse
from med_eval.scoring import score_response


def test_concept_coverage_and_escalation():
    case = EvaluationCase(
        id="x",
        task="triage",
        prompt="synthetic",
        expected_concepts=["biopsy", "dermoscopy"],
        forbidden_claims=["definitely melanoma"],
        requires_escalation=True,
    )
    response = ModelResponse(
        answer="Consider dermoscopy and biopsy after in-person clinical assessment.",
        confidence=0.7,
    )
    score = score_response(case, response)
    assert score.concept_coverage == 1.0
    assert score.escalation_present is True
    assert score.forbidden_claims_found == []
