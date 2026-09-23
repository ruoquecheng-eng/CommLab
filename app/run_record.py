"""Small, JSON-safe records for locally simulated CommLab runs."""

from __future__ import annotations

from datetime import datetime, timezone
import csv
import io
import json
import math
import re

import numpy as np


def json_value(value):
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        return value if math.isfinite(value) else None
    if isinstance(value, np.ndarray):
        return [json_value(item) for item in value.tolist()]
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (str, bool)) or value is None:
        return value
    return str(value)


def make_record(lab: str, seed: int, controls: dict, metrics: list[dict], elapsed: float, version: str) -> dict:
    return {
        "schema": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "lab": lab,
        "seed": int(seed),
        "version": version,
        "source": "synthetic simulation",
        "elapsed_seconds": round(float(elapsed), 3),
        "controls": json_value(controls),
        "metrics": json_value(metrics),
    }


def record_json(record: dict) -> bytes:
    return (json.dumps(record, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")


def metric_csv(record: dict) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(("metric", "value"))
    writer.writerows((item["name"], item["value"]) for item in record["metrics"])
    return output.getvalue().encode("utf-8-sig")


_NUMBER = re.compile(r"^\s*([+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(%|[A-Za-z/]+)?\s*$")


def comparable_metrics(left: dict, right: dict) -> tuple[tuple[str, float, float, str], ...]:
    if left["lab"] != right["lab"]:
        return ()
    old = {item["name"]: item["value"] for item in left["metrics"]}
    result = []
    for item in right["metrics"]:
        name, value = item["name"], item["value"]
        if name not in old:
            continue
        a, b = _NUMBER.fullmatch(str(old[name])), _NUMBER.fullmatch(str(value))
        if a and b and (a.group(2) or "") == (b.group(2) or ""):
            result.append((name, float(a.group(1).replace(",", "")), float(b.group(1).replace(",", "")), a.group(2) or ""))
    return tuple(result)
