#!/usr/bin/env python3
"""Read a prediction ID from the documented Atlas CLI receipt fields.

This helper performs no network calls. It does not infer billing or completion.
It is not a generic parser for MCP, REST, or arbitrary vendor responses.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def extract_id(receipt: Any) -> str:
    if not isinstance(receipt, dict):
        raise ValueError("回执根节点不是 JSON 对象；请核对实际 CLI 输出。")
    values = []
    for key in ("id", "prediction_id"):
        if key not in receipt:
            continue
        value = receipt[key]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"回执中的 {key} 不是非空字符串。")
        value = value.strip()
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError("任务 ID 含控制字符；请核对回执。")
        values.append(value)
    if not values:
        raise ValueError("没有找到已知 CLI 字段 id/prediction_id；受理结果可能未知。")
    if len(set(values)) != 1:
        raise ValueError("id 与 prediction_id 不一致，不能自行选择。")
    return values[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="CLI 保存的 JSON 回执")
    args = parser.parse_args()
    try:
        raw = args.receipt.read_text(encoding="utf-8")
        if not raw.strip():
            raise ValueError("回执为空；这不证明生成未被受理。")
        prediction_id = extract_id(json.loads(raw))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"读取失败：{exc}", file=sys.stderr)
        print("保留回执并核对原请求，不要因此自动重新生成。", file=sys.stderr)
        return 2
    print(prediction_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
