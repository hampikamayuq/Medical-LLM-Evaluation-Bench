from med_eval.adapters import MockModelAdapter
from med_eval.models import EvaluationCase
from med_eval.runner import run_benchmark


def test_runner_returns_report():
    cases = [
        EvaluationCase(
            id="one",
            task="demo",
            prompt="demo",
            expected_concepts=["clinician"],
            requires_escalation=False,
        )
    ]
    report = run_benchmark(cases, MockModelAdapter())
    assert report.cases == 1
    assert report.structured_output_validity == 1.0
