from med_eval.adapters import MockModelAdapter
from med_eval.matrix import markdown_table, run_model_matrix
from med_eval.models import EvaluationCase


def test_matrix_produces_comparable_rows():
    cases = [
        EvaluationCase(
            id="one",
            task="demo",
            prompt="demo",
            expected_concepts=["clinical assessment"],
            requires_escalation=True,
        )
    ]
    rows = run_model_matrix(cases, {"mock-a": MockModelAdapter(), "mock-b": MockModelAdapter()})
    assert len(rows) == 2
    assert rows[0].cases == 1
    assert "mock-a" in markdown_table(rows)
