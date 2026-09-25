from __future__ import annotations

import argparse
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from med_eval.matrix import markdown_table, run_model_matrix, write_csv
from med_eval.ollama_adapter import OllamaAdapter, list_local_models
from med_eval.runner import load_cases


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return 'unknown'


def _write_markdown(path: Path, table: str, model_names: list[str], dataset: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = [
        '# Local Ollama benchmark',
        '',
        f'- Run date (UTC): {datetime.now(timezone.utc).isoformat()}',
        f'- Git commit: {_git_commit()}',
        f'- Dataset: {dataset}',
        f"- Models: {', '.join(model_names)}",
        f'- Platform: {platform.platform()}',
        f'- Machine: {platform.machine()}',
        '',
        '> Latency is hardware-dependent. These metrics do not establish clinical safety.',
        '',
        table,
        '',
    ]
    path.write_text('\n'.join(metadata), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Run the medical LLM benchmark against local Ollama models'
    )
    parser.add_argument('--models', default='models.ollama.example.json')
    parser.add_argument('--dataset', default='data/synthetic_dermatology_cases.json')
    parser.add_argument('--csv', default='results/ollama-latest.csv')
    parser.add_argument('--markdown', default='results/ollama-latest.md')
    parser.add_argument('--base-url', default='http://localhost:11434')
    parser.add_argument('--timeout', type=float, default=180.0)
    args = parser.parse_args()

    specs = json.loads(Path(args.models).read_text(encoding='utf-8'))
    requested_names = [spec['name'] for spec in specs]

    installed = set(list_local_models(args.base_url))
    missing = [name for name in requested_names if name not in installed]
    if missing:
        print('The following Ollama models are not installed:')
        for name in missing:
            print(f'  ollama pull {name}')
        raise SystemExit(2)

    adapters = {
        spec['name']: OllamaAdapter(
            model=spec['name'],
            base_url=args.base_url,
            temperature=float(spec.get('temperature', 0.0)),
            seed=int(spec.get('seed', 42)),
            num_ctx=int(spec.get('num_ctx', 4096)),
            timeout_s=args.timeout,
        )
        for spec in specs
    }

    cases = load_cases(args.dataset)
    rows = run_model_matrix(cases, adapters)
    write_csv(rows, args.csv)

    table = markdown_table(rows)
    _write_markdown(Path(args.markdown), table, requested_names, args.dataset)
    print(table)
    print(f'\nCSV: {args.csv}')
    print(f'Markdown: {args.markdown}')


if __name__ == '__main__':
    main()
