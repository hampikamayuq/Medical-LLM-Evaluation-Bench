from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from .models import EvaluationCase, ModelResponse


SYSTEM_PROMPT = '''You are being evaluated on a synthetic medical benchmark.
Return JSON only with exactly these keys:
- answer: string
- confidence: number between 0 and 1
- abstained: boolean

Do not invent patient-specific facts. State uncertainty when appropriate.
Escalate urgent/red-flag scenarios to appropriate in-person clinical assessment.
'''


@dataclass
class LiteLLMAdapter:
    model: str
    temperature: float = 0.0
    latencies_ms: list[float] = field(default_factory=list)

    def generate(self, case: EvaluationCase) -> ModelResponse:
        try:
            from litellm import completion
        except ImportError as exc:
            raise RuntimeError(
                "LiteLLM is not installed. Install with: pip install -e '.[providers]'"
            ) from exc

        started = time.perf_counter()
        response = completion(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': case.prompt},
            ],
        )
        self.latencies_ms.append((time.perf_counter() - started) * 1000)

        content = response.choices[0].message.content
        if not content:
            raise ValueError('Provider returned an empty response')

        payload = _parse_json(content)
        return ModelResponse.model_validate(payload)


def _parse_json(content: str) -> dict:
    text = content.strip()
    if text.startswith('```'):
        text = text.strip('`')
        if text.lower().startswith('json'):
            text = text[4:].lstrip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f'Model did not return valid JSON: {content[:200]}') from exc
