"""Small local workbench state, separate from release experiment artifacts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from time import sleep
from uuid import uuid4


def _valid_record(item: object) -> bool:
    return (
        isinstance(item, dict)
        and item.get("schema") == 1
        and isinstance(item.get("lab"), str)
        and isinstance(item.get("created_utc"), str)
        and isinstance(item.get("seed"), int)
        and isinstance(item.get("version"), str)
        and isinstance(item.get("controls"), dict)
        and isinstance(item.get("metrics"), list)
        and all(isinstance(metric, dict) and isinstance(metric.get("name"), str) and isinstance(metric.get("value"), str) for metric in item["metrics"])
    )


def default_path() -> Path:
    override = os.environ.get("COMMLAB_WORKBENCH_STATE")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "CommLab" / "workbench-v1.json"
    return Path.home() / ".local" / "share" / "CommLab" / "workbench-v1.json"


def load_state(path: Path | None = None) -> dict:
    target = path or default_path()
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"favorites": [], "recent": [], "records": []}
    if not isinstance(payload, dict):
        return {"favorites": [], "recent": [], "records": []}
    names = lambda key, limit: [item for item in payload.get(key, []) if isinstance(item, str)][:limit] if isinstance(payload.get(key), list) else []
    records = payload.get("records")
    return {
        "favorites": names("favorites", 130),
        "recent": names("recent", 6),
        "records": [item for item in records if _valid_record(item)][:50] if isinstance(records, list) else [],
    }


def save_state(state: dict, path: Path | None = None) -> None:
    target = path or default_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(state, ensure_ascii=False, allow_nan=False), encoding="utf-8")
        for attempt in range(5):
            try:
                temporary.replace(target)
                break
            except PermissionError:
                if attempt == 4:
                    raise
                sleep(0.02)
    finally:
        temporary.unlink(missing_ok=True)
