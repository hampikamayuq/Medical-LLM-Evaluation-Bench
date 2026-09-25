from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .runner import run_benchmark


@dataclass
class MatrixResult:
    model: str
    cases: int
    mean_concept_coverage: float
    forbidden_claim_rate: float
    safety_flag_rate: float
    structured_output_validity: float


def run_model_matrix(cases, adapters: dict[str, object]) -> list[MatrixResult]:
    rows: list[MatrixResult] = []
    for name, adapter in adapters.items():
        report = run_benchmark(cases, adapter)
        rows.append(MatrixResult(
            model=name,
            cases=report.cases,
            mean_concept_coverage=report.mean_concept_coverage,
            forbidden_claim_rate=report.forbidden_claim_rate,
            safety_flag_rate=report.safety_flag_rate,
            structured_output_validity=report.structured_output_validity,
        ))
    return rows


def write_csv(rows: list[MatrixResult], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MatrixResult.__annotations__))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def markdown_table(rows: list[MatrixResult]) -> str:
    header = (
        "| Model | Cases | Concept coverage | Forbidden-claim rate | Safety-flag rate | Structured output |\n"
        "|---|---:|---:|---:|---:|---:|"
    )
    body = [
        (f"| {r.model} | {r.cases} | {r.mean_concept_coverage:.3f} | "
         f"{r.forbidden_claim_rate:.3f} | {r.safety_flag_rate:.3f} | "
         f"{r.structured_output_validity:.3f} |")
        for r in rows
    ]
    return "\n".join([header, *body])
