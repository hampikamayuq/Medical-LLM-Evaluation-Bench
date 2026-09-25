import json

from med_eval.models import EvaluationCase
from med_eval.ollama_adapter import OllamaAdapter, _parse_model_response


def test_parse_model_response():
    response = _parse_model_response(
        json.dumps(
            {
                'answer': 'Recommend clinical assessment.',
                'confidence': 0.8,
                'abstained': False,
            }
        )
    )
    assert response.confidence == 0.8
    assert response.abstained is False


def test_ollama_adapter_with_mocked_transport(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            payload = {
                'message': {
                    'content': json.dumps(
                        {
                            'answer': 'Clinical assessment is appropriate.',
                            'confidence': 0.75,
                            'abstained': False,
                        }
                    )
                },
                'total_duration': 10_000_000,
                'eval_count': 12,
            }
            return json.dumps(payload).encode('utf-8')

    monkeypatch.setattr(
        'med_eval.ollama_adapter.urlopen',
        lambda request, timeout: FakeResponse(),
    )

    adapter = OllamaAdapter(model='local-test')
    case = EvaluationCase(id='demo', task='triage', prompt='synthetic')
    response = adapter.generate(case)

    assert response.answer == 'Clinical assessment is appropriate.'
    assert adapter.latencies_ms
    assert adapter.ollama_total_duration_ms == [10.0]
    assert adapter.eval_token_counts == [12]
