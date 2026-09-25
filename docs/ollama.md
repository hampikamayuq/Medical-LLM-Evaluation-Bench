# Running the benchmark locally with Ollama

This is the default keyless path for real-model evaluation.

## 1. Install and start Ollama

Install Ollama using its official installer for your operating system, then verify:

```bash
ollama --version
ollama serve
```

If the desktop application already runs the service, a separate `ollama serve` process may not be necessary.

## 2. Pull the benchmark models

The example configuration uses compact models that are practical for local experimentation:

```bash
ollama pull qwen3:4b-instruct
ollama pull gemma3:4b
ollama pull llama3.2:3b
```

You can replace these with any models available in your local Ollama installation.

## 3. Install the benchmark

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 4. Run the comparison

```bash
python scripts/run_ollama_matrix.py
```

Outputs:

- `results/ollama-latest.csv`
- `results/ollama-latest.md`

## Metrics

The local matrix reports concept coverage, forbidden-claim rate, safety-flag rate, structured-output validity, abstention rate, adapter/output error rate, mean wall-clock latency, and P95 wall-clock latency.

Latency is specific to the machine, model quantization, thermal state, context size, model cache state and Ollama version. Do not compare latency across different computers without recording the hardware and run conditions.

## Reproducibility

The example configuration fixes temperature to 0 and seed to 42. Exact reproducibility is not guaranteed across model builds, quantizations, hardware backends or Ollama versions.

## Privacy

The default base URL is `http://localhost:11434`, so prompts remain on the local Ollama service. Do not change the base URL to a remote host unless its data-handling implications are understood.
