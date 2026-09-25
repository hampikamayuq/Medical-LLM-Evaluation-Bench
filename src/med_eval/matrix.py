from __future__ import annotations

import csv
import math
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
    abstention_rate: float
    error_rate: float
    mean_latency_ms: float | None
    p95_latency_ms: float | None


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(q * len(ordered)) - 1)
    return round(ordered[index], 1)


def run_model_matrix(cases, adapters: dict[str, object]) -> list[MatrixResult]:
    rows: list[MatrixResult] = []
    for name, adapter in adapters.items():
        if hasattr(adapter, "latencies_ms"):
            adapter.latencies_ms.clear()

        report = run_benchmark(cases, adapter)
        latencies = list(getattr(adapter, "latencies_ms", []))

        rows.append(
            MatrixResult(
                model=name,
                cases=report.cases,
                mean_concept_coverage=report.mean_concept_coverage,
                forbidden_claim_rate=report.forbidden_claim_rate,
                safety_flag_rate=report.safety_flag_rate,
                structured_output_validity=report.structured_output_validity,
                abstention_rate=report.abstention_rate,
                error_rate=report.error_rate,
                mean_latency_ms=round(sum(latencies) / len(latencies), 1) if latencies else None,
                p95_latency_ms=_percentile(latencies, 0.95),
            )
        )
    return rows


def write_csv(rows: list[MatrixResult], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MatrixResult.__annotations__))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def _fmt(value: float | None, digits: int = 3) -> str:
    return "-" if value is None else f"{value:.{digits}f}"


def markdown_table(rows: list[MatrixResult]) -> str:
    header = (
        "| Model | Cases | Concept coverage | Forbidden claims | Safety flags | "
        "Structured output | Abstention | Errors | Mean latency ms | P95 latency ms |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    )
    body = [
        (
            f"| {r.model} | {r.cases} | {r.mean_concept_coverage:.3f} | "
            f"{r.forbidden_claim_rate:.3f} | {r.safety_flag_rate:.3f} | "
            f"{r.structured_output_validity:.3f} | {r.abstention_rate:.3f} | "
            f"{r.error_rate:.3f} | {_fmt(r.mean_latency_ms, 1)} | {_fmt(r.p95_latency_ms, 1)} |"
        )
        for r in rows
    ]
    return "\n".join([header, *body])
