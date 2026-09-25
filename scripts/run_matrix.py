from __future__ import annotations

import argparse
import json
from pathlib import Path

from med_eval.litellm_adapter import LiteLLMAdapter
from med_eval.matrix import markdown_table, run_model_matrix, write_csv
from med_eval.runner import load_cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a comparative LLM benchmark matrix")
    parser.add_argument("--models", default="models.example.json")
    parser.add_argument("--dataset", default="data/synthetic_dermatology_cases.json")
    parser.add_argument("--csv", default="results/latest.csv")
    args = parser.parse_args()

    model_specs = json.loads(Path(args.models).read_text(encoding="utf-8"))
    adapters = {
        spec["name"]: LiteLLMAdapter(
            model=spec["name"],
            temperature=float(spec.get("temperature", 0.0)),
        )
        for spec in model_specs
    }

    cases = load_cases(args.dataset)
    rows = run_model_matrix(cases, adapters)
    write_csv(rows, args.csv)
    print(markdown_table(rows))


if __name__ == "__main__":
    main()
