from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import EvaluationCase, ModelResponse


SYSTEM_PROMPT = '''You are being evaluated on a synthetic medical benchmark.
Return JSON only with exactly these keys:
- answer: string
- confidence: number between 0 and 1
- abstained: boolean

Do not invent patient-specific facts. State uncertainty when appropriate.
Escalate urgent or red-flag scenarios to appropriate in-person clinical assessment.
'''


def _request_json(
    url: str,
    *,
    payload: dict | None = None,
    timeout_s: float = 180.0,
) -> dict:
    body = None if payload is None else json.dumps(payload).encode('utf-8')
    request = Request(
        url,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='GET' if payload is None else 'POST',
    )
    try:
        with urlopen(request, timeout=timeout_s) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'Ollama HTTP {exc.code}: {detail[:300]}') from exc
    except URLError as exc:
        raise RuntimeError(
            "Cannot reach Ollama. Start it with 'ollama serve' and verify the base URL."
        ) from exc


def list_local_models(base_url: str = 'http://localhost:11434') -> list[str]:
    payload = _request_json(f"{base_url.rstrip('/')}/api/tags", timeout_s=10.0)
    return [item['name'] for item in payload.get('models', []) if 'name' in item]


def _parse_model_response(content: str) -> ModelResponse:
    text = content.strip()
    if text.startswith('```'):
        text = text.strip('`')
        if text.lower().startswith('json'):
            text = text[4:].lstrip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f'Model did not return valid JSON: {content[:240]}') from exc
    return ModelResponse.model_validate(payload)


@dataclass
class OllamaAdapter:
    model: str
    base_url: str = 'http://localhost:11434'
    temperature: float = 0.0
    seed: int = 42
    num_ctx: int = 4096
    timeout_s: float = 180.0
    latencies_ms: list[float] = field(default_factory=list)
    ollama_total_duration_ms: list[float] = field(default_factory=list)
    eval_token_counts: list[int] = field(default_factory=list)

    def generate(self, case: EvaluationCase) -> ModelResponse:
        payload = {
            'model': self.model,
            'stream': False,
            'format': 'json',
            'messages': [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': case.prompt},
            ],
            'options': {
                'temperature': self.temperature,
                'seed': self.seed,
                'num_ctx': self.num_ctx,
            },
        }

        started = time.perf_counter()
        result = _request_json(
            f"{self.base_url.rstrip('/')}/api/chat",
            payload=payload,
            timeout_s=self.timeout_s,
        )
        self.latencies_ms.append((time.perf_counter() - started) * 1000)

        if isinstance(result.get('total_duration'), int):
            self.ollama_total_duration_ms.append(result['total_duration'] / 1_000_000)
        if isinstance(result.get('eval_count'), int):
            self.eval_token_counts.append(result['eval_count'])

        try:
            content = result['message']['content']
        except (KeyError, TypeError) as exc:
            raise ValueError(f'Unexpected Ollama response shape: {result}') from exc

        return _parse_model_response(content)
