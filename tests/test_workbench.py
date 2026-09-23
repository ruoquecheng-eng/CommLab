import ast
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from threading import Barrier

import numpy as np

from app.lab_catalog import ALL_LABS, GROUPS, find_labs, group_for, recent_labs
from app.run_record import comparable_metrics, json_value, make_record, metric_csv, record_json
from app.workbench import Controls, captured_columns
from app.local_state import load_state, save_state


def test_catalog_matches_all_existing_dashboard_modes():
    tree = ast.parse((Path(__file__).parents[1] / "app" / "dashboard.py").read_text(encoding="utf-8"))
    branches = {node.comparators[0].value for node in ast.walk(tree) if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) and node.left.id == "mode" and len(node.comparators) == 1 and isinstance(node.comparators[0], ast.Constant) and isinstance(node.comparators[0].value, str)}
    assert len(ALL_LABS) == 130
    assert set(ALL_LABS) == branches | {"Water-Filling"}
    assert len(ALL_LABS) == len(set(ALL_LABS))
    assert {group_for(name) for name in ALL_LABS} == set(GROUPS)


def test_discovery_and_recent_ignore_stale_names():
    assert "OFDM Link" in find_labs(" ofdm   link ")
    assert "OFDM Link" in find_labs("receiver", group="Waveform & receiver")
    assert "OFDM Link" in find_labs("波形")
    assert find_labs("not-a-real-experiment") == ()
    assert recent_labs(["missing", "OFDM Link", "OFDM Link", "Phase Noise"]) == ("OFDM Link", "Phase Noise")


def test_json_record_and_metric_compatibility():
    assert json_value(np.array([np.float64(1), np.float64(float("nan"))])) == [1, None]
    first = make_record("OFDM Link", 2026, {"SNR": np.float64(15.0)}, [{"name": "BER", "value": "1.0e-3"}, {"name": "EVM", "value": "2.0%"}], .12, "3.7.1")
    second = make_record("OFDM Link", 2027, {}, [{"name": "BER", "value": "2.0e-3"}, {"name": "EVM", "value": "3.0%"}], .14, "3.7.1")
    assert comparable_metrics(first, second) == (("BER", .001, .002, ""), ("EVM", 2.0, 3.0, "%"))
    assert comparable_metrics(first, {**second, "lab": "Phase Noise"}) == ()
    assert comparable_metrics({**first, "metrics": [{"name": "Bits", "value": "9,600"}]}, {**second, "metrics": [{"name": "Bits", "value": "10,200"}]}) == (("Bits", 9600.0, 10200.0, ""),)
    assert b'"source": "synthetic simulation"' in record_json(first)
    assert b"BER" in metric_csv(first)


def test_ui_capture_delegates_without_changing_values():
    class Form:
        def slider(self, *args, **kwargs):
            return np.float64(2.5)

    controls = Controls(Form())
    assert controls.slider("SNR", 0, 5) == 2.5
    assert controls.values["SNR"] == 2.5

    class Column:
        def metric(self, label, value, *args, **kwargs):
            return (label, value)

    class Streamlit:
        def columns(self, n):
            return [Column() for _ in range(n)]

    metrics = []
    column, = captured_columns(Streamlit(), metrics)(1)
    assert column.metric("BER", "1e-3") == ("BER", "1e-3")
    assert metrics == [{"name": "BER", "value": "1e-3"}]


def test_local_state_round_trip_and_corrupt_fallback(tmp_path):
    path = tmp_path / "中文" / "workbench-v1.json"
    assert load_state(path)["records"] == []
    save_state({"favorites": ["OFDM Link"], "recent": ["OFDM Link"], "records": [make_record("OFDM Link", 5, {}, [], 0.1, "3.7.1")]}, path)
    assert load_state(path)["records"][0]["seed"] == 5
    path.write_text("{bad", encoding="utf-8")
    assert load_state(path)["favorites"] == []


def test_local_state_ignores_incomplete_run_records(tmp_path):
    path = tmp_path / "workbench-v1.json"
    valid = make_record("OFDM Link", 2026, {}, [{"name": "BER", "value": "0.01"}], 0.1, "3.7.1")
    incomplete = {"schema": 1, "lab": "OFDM Link", "metrics": [{"name": "BER"}]}
    path.write_text(json.dumps({"favorites": ["OFDM Link"], "recent": [], "records": [incomplete, valid]}), encoding="utf-8")
    state = load_state(path)
    assert state["favorites"] == ["OFDM Link"]
    assert state["records"] == [valid]


def test_concurrent_local_state_saves_keep_a_valid_file(monkeypatch, tmp_path):
    path = tmp_path / "workbench-v1.json"
    barrier = Barrier(2)
    staging_paths = []
    original_write_text = Path.write_text

    def write_text_and_wait(target, *args, **kwargs):
        result = original_write_text(target, *args, **kwargs)
        if target.suffix == ".tmp":
            staging_paths.append(target)
            barrier.wait(timeout=5)
        return result

    monkeypatch.setattr(Path, "write_text", write_text_and_wait)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(save_state, {"favorites": [name], "recent": [], "records": []}, path) for name in ("OFDM Link", "Phase Noise")]
        for future in futures:
            future.result()
    assert len(set(staging_paths)) == 2
    assert load_state(path)["favorites"] in (["OFDM Link"], ["Phase Noise"])


def test_local_state_save_retries_temporary_windows_replace_conflict(monkeypatch, tmp_path):
    path = tmp_path / "workbench-v1.json"
    original_replace = Path.replace
    calls = 0

    def replace_with_one_conflict(source, target):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise PermissionError(5, "temporary sharing violation")
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", replace_with_one_conflict)
    save_state({"favorites": ["OFDM Link"], "recent": [], "records": []}, path)
    assert load_state(path)["favorites"] == ["OFDM Link"]
