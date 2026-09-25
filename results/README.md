# Benchmark results

This directory stores outputs from both local Ollama runs and optional hosted-model runs.

## Local Ollama matrix — recommended keyless path

Run:

```bash
python scripts/run_ollama_matrix.py
```

Generated files:

- `ollama-latest.csv`
- `ollama-latest.md`

The Markdown report records run date, Git commit, dataset, model identifiers and host platform. Latency is machine-dependent and should only be compared within a controlled run.

## Synthetic harness smoke test

The internal deterministic adapter verifies that the evaluation pipeline works. It is not a real-model benchmark.

| Adapter | Purpose | Cases | Expected status |
|---|---|---:|---|
| MockModelAdapter | Pipeline smoke test | 6 | Deterministic |

## Metrics

| Metric | Direction | Interpretation |
|---|---|---|
| Concept coverage | Higher | Expected concepts found in the answer |
| Forbidden-claim rate | Lower | Case-specific claims that must not appear |
| Safety-flag rate | Lower | Clearly unsafe output patterns |
| Structured-output validity | Higher | Valid response schema |
| Abstention rate | Context-dependent | Model explicitly declines or defers |
| Error rate | Lower | Transport or malformed-output failures |
| Mean/P95 latency | Lower | Wall-clock response latency on the same hardware |

## Hosted-model matrix

Hosted providers remain optional. If credentials are available, use `scripts/run_matrix.py` with the LiteLLM adapter.

Benchmark scores do not establish clinical safety or regulatory fitness. Any clinically consequential interpretation requires qualified human review.
