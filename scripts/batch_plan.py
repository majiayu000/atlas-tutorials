#!/usr/bin/env python3
"""Prepare one local plan per SKU. Never contacts Atlas or submits a job."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import re
import sys
from run_job import prepare, validate_config


def build_rows(csv_path: Path, model: str, reference_field: str | None, max_jobs: int) -> list[tuple[str, dict]]:
    if not 1 <= max_jobs <= 1000: raise ValueError('max-jobs must be 1..1000')
    with csv_path.open(encoding='utf-8-sig', newline='') as table:
        rows = list(csv.DictReader(table))
    if not rows or len(rows) > max_jobs: raise ValueError('empty table or row count exceeds max-jobs')
    result, seen = [], set()
    for row in rows:
        sku = row.get('sku', '')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', sku) or sku.lower() in seen:
            raise ValueError('SKU must be unique and path-safe, including on case-insensitive filesystems')
        seen.add(sku.lower())
        prompt = row.get('prompt', '').strip()
        if not prompt: raise ValueError(f'empty prompt for {sku}')
        params = {'prompt': prompt}
        url = row.get('reference_url', '').strip()
        if url:
            if not url.startswith('https://') or not reference_field:
                raise ValueError('reference URL needs HTTPS and an explicitly verified --reference-field')
            if reference_field in {'prompt', 'model'}: raise ValueError('invalid reference field')
            params[reference_field] = url
        cfg = validate_config({'kind': 'image', 'model': model, 'params': params})
        result.append((sku, cfg))
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--csv', type=Path, required=True); p.add_argument('--model', required=True)
    p.add_argument('--out', type=Path, required=True); p.add_argument('--max-jobs', type=int, default=3)
    p.add_argument('--reference-field', help='Exact schema field accepting a single URL; arrays require a custom adapter')
    a = p.parse_args()
    try:
        rows = build_rows(a.csv, a.model, a.reference_field, a.max_jobs)
        a.out.mkdir(parents=True, exist_ok=False)
        records = []
        for sku, cfg in rows:
            cfg_path = a.out / f'{sku}.config.json'
            cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            prepare(cfg_path, a.out / sku)
            records.append({'sku': sku, 'run_dir': sku, 'state': 'prepared', 'submitted': False})
        (a.out / 'batch.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Prepared {len(records)} local plans. No requests sent. Inspect and approve each job separately.')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f'Error: {e}', file=sys.stderr); return 2

if __name__ == '__main__': raise SystemExit(main())
