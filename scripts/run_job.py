#!/usr/bin/env python3
"""An educational, local-first Atlas CLI job recorder. No automatic paid retries."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any
from receipt_id import extract_id

SUCCESS = {'completed', 'succeeded'}
FAILED = {'failed', 'timeout', 'error', 'cancelled', 'canceled'}
PENDING = {'starting', 'processing', 'queued', 'pending', 'running'}


def reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    if path.stat().st_size > 4 * 1024 * 1024:
        raise ValueError('configuration/receipt exceeds 4 MiB')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=reject_duplicates,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f'invalid JSON number: {x}')))


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def save(path: Path, value: Any, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as file:
            json.dump(value, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write('\n'); file.flush(); os.fsync(file.fileno())
        return
    tmp = path.with_name(path.name + f'.tmp-{os.getpid()}-{time.time_ns()}')
    try:
        save(tmp, value, exclusive=True)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def validate_config(data: Any) -> dict:
    if not isinstance(data, dict) or set(data) - {'kind', 'model', 'params'}:
        raise ValueError('config must contain only kind/model/params')
    if data.get('kind') not in {'image', 'video', 'audio', '3d'}:
        raise ValueError('kind must be image/video/audio/3d')
    model = data.get('model')
    if (not isinstance(model, str) or not model.strip() or model != model.strip()
            or model.startswith('-') or any(ord(c) < 33 for c in model)
            or any(x in model.lower() for x in ('replace_', 'placeholder', '替换', '填入'))):
        raise ValueError('choose an actual, discovered model ID before preparing')
    params = data.get('params')
    if not isinstance(params, dict) or not params:
        raise ValueError('params must be a nonempty object from the actual model schema')
    if any(k.lower() in {'model', 'authorization', 'api_key', 'token', 'access_token'} for k in params):
        raise ValueError('do not override model or put credentials in params')
    # This wrapper intentionally uses approved URL inputs. Local @file mapping varies by model.
    def check(value):
        if isinstance(value, dict):
            for v in value.values(): check(v)
        elif isinstance(value, list):
            for v in value: check(v)
        elif isinstance(value, str) and value.startswith('@'):
            raise ValueError('wrapper requires pre-authorized URLs, not local @file inputs; see tutorial 13')
    check(params)
    canonical(data)
    return data


def classify(receipt: Any) -> str:
    if not isinstance(receipt, dict): return 'unknown'
    status = receipt.get('status')
    if not isinstance(status, str): return 'unknown'
    status = status.lower()
    if status in SUCCESS: return 'remote_succeeded'
    if status in FAILED: return 'remote_failed'
    if status in PENDING: return 'pending'
    return 'unknown'


def resolve_binary(value: str) -> str:
    resolved = shutil.which(value)
    if not resolved:
        raise ValueError('Atlas CLI not found; use --atlas /absolute/path/to/atlas when needed')
    return str(Path(resolved).resolve())


def prepare(config_path: Path, run_dir: Path) -> dict:
    config = validate_config(load_json(config_path))
    run_dir = run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    record = {'format': 1, 'created_unix': time.time(), 'config': config, 'config_sha256': digest(config)}
    save(run_dir / 'plan.json', record, exclusive=True)
    save(run_dir / 'params.json', config['params'], exclusive=True)
    return record


def read_plan(run_dir: Path) -> dict:
    plan = load_json(run_dir / 'plan.json')
    config = validate_config(plan['config'])
    if digest(config) != plan.get('config_sha256'):
        raise ValueError('plan hash mismatch; do not silently change an existing operation')
    if load_json(run_dir / 'params.json') != config['params']:
        raise ValueError('params.json differs from the recorded plan')
    return plan


def generation_args(config: dict, run_dir: Path) -> list[str]:
    return ['generate', config['kind'], config['model'], '--params-json', '@' + str((run_dir / 'params.json').resolve())]


def invoke(binary: str, args: list[str], run_dir: Path, timeout: float) -> tuple[int | None, str, str]:
    env = os.environ.copy()
    env['ATLAS_AUTO_UPDATE'] = '0'
    try:
        result = subprocess.run([binary, *args], cwd=run_dir, env=env, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        def text(x): return x.decode('utf-8', 'replace') if isinstance(x, bytes) else (x or '')
        return None, text(exc.stdout), text(exc.stderr) + '\nLocal subprocess timeout; remote acceptance may be unknown.'


def submit(run_dir: Path, binary: str, approve: bool, timeout: float = 120) -> dict:
    plan = read_plan(run_dir)
    if not approve: raise ValueError('billable submission requires explicit --approve')
    # This exclusive marker is never automatically removed, even on crashes/errors.
    save(run_dir / 'attempt.json', {'config_sha256': plan['config_sha256'], 'started_unix': time.time(),
                                  'state': 'submission_may_be_unknown'}, exclusive=True)
    code, out, err = invoke(binary, generation_args(plan['config'], run_dir) + ['--no-wait', '--json'], run_dir, timeout)
    # Raw receipts may contain private prompts/URLs. Keep these local.
    (run_dir / 'submit.stdout.txt').write_text(out, encoding='utf-8')
    (run_dir / 'submit.stderr.txt').write_text(err, encoding='utf-8')
    result = {'cli_exit_code': code, 'state': 'unknown', 'prediction_id': None}
    try:
        receipt = json.loads(out, object_pairs_hook=reject_duplicates)
        save(run_dir / 'submit.json', receipt)
        result['prediction_id'] = extract_id(receipt)
        result['state'] = classify(receipt)
        if result['state'] == 'unknown': result['state'] = 'accepted_status_unknown'
    except (ValueError, TypeError):
        pass
    save(run_dir / 'submission-state.json', result)
    return result


def observe(run_dir: Path, binary: str, wait: bool, wait_seconds: int) -> dict:
    read_plan(run_dir)
    state = load_json(run_dir / 'submission-state.json')
    pred_id = state.get('prediction_id')
    if not pred_id or not isinstance(pred_id, str) or pred_id.startswith('-'):
        raise ValueError('no reliable prediction ID: reconcile first, never automatically submit again')
    args = ['generate', 'wait' if wait else 'get', pred_id, '--json']
    if wait: args += ['--timeout', f'{wait_seconds}s']
    code, out, err = invoke(binary, args, run_dir, wait_seconds + 30 if wait else 90)
    stamp = str(time.time_ns())
    directory = run_dir / 'observations'; directory.mkdir(exist_ok=True)
    (directory / f'{stamp}.stdout.txt').write_text(out, encoding='utf-8')
    (directory / f'{stamp}.stderr.txt').write_text(err, encoding='utf-8')
    result = {'cli_exit_code': code, 'prediction_id': pred_id, 'state': 'unknown', 'observation': stamp}
    try:
        receipt = json.loads(out, object_pairs_hook=reject_duplicates)
        save(directory / f'{stamp}.json', receipt)
        if not isinstance(receipt, dict): raise ValueError('unexpected receipt')
        if 'id' in receipt or 'prediction_id' in receipt:
            if extract_id(receipt) != pred_id: raise ValueError('prediction ID mismatch')
        result['state'] = classify(receipt)
        result['saved_files'] = receipt.get('saved_files', [])
    except (ValueError, TypeError):
        result['state'] = 'unknown'
    save(run_dir / 'latest-observation.json', result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'preview', 'submit', 'get', 'wait', 'inspect'])
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--atlas', default='atlas')
    parser.add_argument('--approve', action='store_true')
    parser.add_argument('--wait-seconds', type=int, default=600)
    args = parser.parse_args()
    try:
        run_dir = args.run_dir.resolve()
        if not 1 <= args.wait_seconds <= 3600: raise ValueError('wait-seconds must be 1..3600')
        if args.action == 'prepare':
            if args.config is None: raise ValueError('prepare requires --config')
            result = prepare(args.config, run_dir)
        elif args.action == 'inspect':
            result = {'plan': read_plan(run_dir), 'attempt_exists': (run_dir / 'attempt.json').exists()}
            for name in ['submission-state.json', 'latest-observation.json']:
                if (run_dir / name).exists(): result[name] = load_json(run_dir / name)
        else:
            binary = resolve_binary(args.atlas)
            plan = read_plan(run_dir)
            if args.action == 'preview':
                code, out, err = invoke(binary, generation_args(plan['config'], run_dir) + ['--explain', '--json'], run_dir, 90)
                (run_dir / 'preview.stdout.txt').write_text(out, encoding='utf-8')
                (run_dir / 'preview.stderr.txt').write_text(err, encoding='utf-8')
                result = {'cli_exit_code': code, 'billable_submission': False, 'preview_file': 'preview.stdout.txt'}
                print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if code == 0 else 2
            if args.action == 'submit': result = submit(run_dir, binary, args.approve)
            else: result = observe(run_dir, binary, args.action == 'wait', args.wait_seconds)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        state = result.get('state')
        if state == 'remote_failed': return 4
        if state in {'unknown', 'accepted_status_unknown'}: return 2
        if state == 'pending': return 3
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Error: {exc}. Keep existing records; do not delete attempt.json to retry.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
