# Keyless Ollama benchmark — GitHub Actions

- Run date (UTC): 2026-09-25T18:31:12.754945+00:00
- Environment: GitHub-hosted ubuntu-latest runner, CPU inference
- Dataset: data/synthetic_dermatology_cases.json
- Temperature: 0.0
- Seed: 42
- Context: 4096 tokens

> Latency is specific to the GitHub-hosted runner and must not be compared directly with local workstation latency.
> These benchmark metrics do not establish clinical safety or medical-device performance.

| Model | Cases | Concept coverage | Forbidden claims | Safety flags | Structured output | Abstention | Errors | Mean latency ms | P95 latency ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3:4b-instruct | 6 | 0.445 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 23673.7 | 40012.8 |
| gemma3:4b | 6 | 0.389 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 26514.7 | 45964.0 |
| llama3.2:3b | 6 | 0.333 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 7146.6 | 10076.2 |
