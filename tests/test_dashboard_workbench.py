"""Run the real Streamlit page in process to catch widget and record regressions."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.local_state import save_state


DASHBOARD = Path(__file__).parents[1] / "app" / "dashboard.py"


def start_app(monkeypatch, tmp_path):
    monkeypatch.setenv("COMMLAB_WORKBENCH_STATE", str(tmp_path / "workbench-v1.json"))
    app = AppTest.from_file(str(DASHBOARD), default_timeout=40).run()
    assert not app.exception
    return app


def test_default_lab_and_submitted_controls(monkeypatch, tmp_path):
    app = start_app(monkeypatch, tmp_path)
    assert app.selectbox(key="lab_selection").value == "OFDM Link"
    assert app.metric[1].value == "16.03%"
    assert app.session_state["lab_records"][0]["controls"]["Sample-domain SNR (dB)"] == 15.0
    app.slider[0].set_value(25.0)
    app.button(key="FormSubmitter:parameters:OFDM Link:0-运行实验 · 更新结果").click().run()
    assert not app.exception
    assert app.metric[1].value != "16.03%"
    assert app.session_state["lab_records"][0]["controls"]["Sample-domain SNR (dB)"] == 25.0
    assert len(app.session_state["lab_records"]) == 2
    replay_value = app.metric[1].value
    app.button(key="FormSubmitter:parameters:OFDM Link:0-运行实验 · 更新结果").click().run()
    assert not app.exception
    assert app.metric[1].value == replay_value
    assert len(app.session_state["lab_records"]) == 3


def test_find_change_mode_and_restore_defaults(monkeypatch, tmp_path):
    app = start_app(monkeypatch, tmp_path)
    app.text_input(key="lab_query").set_value("phase noise").run()
    assert not app.exception
    assert app.selectbox(key="lab_selection").options == ["Phase Noise"]
    app.selectbox(key="lab_selection").set_value("Phase Noise").run()
    assert not app.exception
    assert app.session_state["lab_records"][0]["lab"] == "Phase Noise"
    app.number_input[0].set_value(404)
    app.button(key="FormSubmitter:parameters:Phase Noise:0-运行实验 · 更新结果").click().run()
    assert app.session_state["lab_records"][0]["seed"] == 404
    next(button for button in app.button if button.label == "恢复当前实验默认参数").click().run()
    assert not app.exception
    assert app.number_input[0].value == 2026


def test_no_matches_stays_recoverable(monkeypatch, tmp_path):
    app = start_app(monkeypatch, tmp_path)
    app.text_input(key="lab_query").set_value("not-a-real-lab").run()
    assert not app.exception
    assert all(item.key != "lab_selection" for item in app.selectbox)
    app.text_input(key="lab_query").set_value("").run()
    assert app.selectbox(key="lab_selection").value == "OFDM Link"


def test_search_reports_matching_lab_count(monkeypatch, tmp_path):
    app = start_app(monkeypatch, tmp_path)
    app.text_input(key="lab_query").set_value("phase noise").run()
    assert not app.exception
    assert any("匹配 1 / 130 个实验" in item.value for item in app.caption)


@pytest.mark.parametrize("name", ["2x2 MIMO Detection", "ISAC MUSIC", "AirComp Aggregation", "Water-Filling"])
def test_representative_lab_groups_render(monkeypatch, tmp_path, name):
    app = start_app(monkeypatch, tmp_path)
    app.text_input(key="lab_query").set_value(name).run()
    app.selectbox(key="lab_selection").set_value(name).run()
    assert not app.exception
    assert app.session_state["lab_records"][0]["lab"] == name
    assert any(item.value == name for item in app.subheader)


def test_favorite_survives_new_session(monkeypatch, tmp_path):
    app = start_app(monkeypatch, tmp_path)
    app.toggle(key="favorite:OFDM Link").set_value(True).run()
    assert not app.exception
    assert "OFDM Link" in app.session_state["lab_favorites"]
    reopened = start_app(monkeypatch, tmp_path)
    assert reopened.toggle(key="favorite:OFDM Link").value is True


def test_new_session_restores_last_used_lab(monkeypatch, tmp_path):
    save_state({"favorites": [], "recent": ["Phase Noise"], "records": []}, tmp_path / "workbench-v1.json")
    app = start_app(monkeypatch, tmp_path)
    assert app.selectbox(key="lab_selection").value == "Phase Noise"
    assert app.session_state["lab_records"][0]["lab"] == "Phase Noise"


def test_comparison_shows_signed_change_with_percentage_points(monkeypatch, tmp_path):
    app = start_app(monkeypatch, tmp_path)
    app.slider[0].set_value(25.0)
    app.button(key="FormSubmitter:parameters:OFDM Link:0-运行实验 · 更新结果").click().run()
    assert not app.exception
    table = app.dataframe[0].value
    assert "变化" in table.columns
    evm = table.loc[table["指标"] == "RMS EVM"].iloc[0]
    assert evm["变化"].endswith(" pp")
    assert evm["变化"].startswith("-")
