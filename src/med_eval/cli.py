from __future__ import annotations

import argparse

from .adapters import MockModelAdapter
from .runner import load_cases, run_benchmark


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic medical LLM benchmark")
    parser.add_argument("--dataset", default="data/synthetic_dermatology_cases.json")
    args = parser.parse_args()

    cases = load_cases(args.dataset)
    report = run_benchmark(cases, MockModelAdapter())
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
