from datetime import datetime
from pathlib import Path
import subprocess

from desktop import launcher


def test_source_resource_root_contains_dashboard():
    root=launcher.resource_root()
    assert (root/"app"/"dashboard.py").exists()


def test_source_resource_root_supports_unicode_install_path(monkeypatch, tmp_path):
    root = tmp_path / "中文 用户" / "CommLab"
    monkeypatch.setattr(launcher, "__file__", str(root / "desktop" / "launcher.py"))
    assert launcher.resource_root() == root.resolve()


def test_frozen_resource_root_supports_unicode_install_path(monkeypatch, tmp_path):
    root = tmp_path / "中文 用户" / "CommLab"
    monkeypatch.setattr(launcher.sys, "frozen", True, raising=False)
    monkeypatch.setattr(launcher.sys, "_MEIPASS", str(root), raising=False)
    assert launcher.resource_root() == root.resolve()


def test_dashboard_path_can_use_explicit_root(tmp_path):
    assert launcher.dashboard_path(tmp_path)==tmp_path/"app"/"dashboard.py"


def test_free_port_is_valid():
    assert 1024<launcher.find_free_port()<65536


def test_streamlit_flags_are_local_and_headless():
    flags=launcher.streamlit_flags(8765)
    assert flags["server.address"]=="127.0.0.1"
    assert flags["global.developmentMode"] is False
    assert flags["server.port"]==8765
    assert flags["server.headless"] is True
    assert flags["browser.gatherUsageStats"] is False


def test_source_server_command_reenters_launcher():
    command=launcher.server_command(8765)
    assert command[-2:]==["--server-child","8765"]
    assert Path(command[1]).name=="launcher.py"


class _RunningProcess:
    def __init__(self): self.terminated=False; self.killed=False
    def poll(self): return None
    def terminate(self): self.terminated=True
    def wait(self,timeout):
        if not self.killed: raise subprocess.TimeoutExpired("fake",timeout)
        return 0
    def kill(self): self.killed=True


def test_stop_server_escalates_after_timeout():
    process=_RunningProcess(); launcher.stop_server(process,timeout=.01)
    assert process.terminated and process.killed


class _ExitedProcess:
    def poll(self): return 2


def test_wait_until_ready_stops_if_child_exits():
    assert launcher.wait_until_ready(_ExitedProcess(),8765,timeout=.01) is False


def test_user_data_dir_uses_local_appdata(monkeypatch,tmp_path):
    monkeypatch.setenv("LOCALAPPDATA",str(tmp_path))
    assert launcher.user_data_dir()==tmp_path/"CommLab"


def test_user_data_dir_supports_unicode_path(monkeypatch,tmp_path):
    local_appdata = tmp_path / "中文 用户"
    monkeypatch.setenv("LOCALAPPDATA", str(local_appdata))
    assert launcher.user_data_dir() == local_appdata / "CommLab"


def test_launch_log_path_is_attempt_specific(tmp_path, monkeypatch):
    monkeypatch.setattr(launcher.os, "getpid", lambda: 4321)
    stamp = datetime(2026, 9, 4, 12, 34, 56, 789000)
    path = launcher.launch_log_path(tmp_path, 8765, stamp)
    assert path == tmp_path / "desktop-20260904-123456-789000-p4321-port8765.log"


def test_log_tail_and_diagnostic_report(tmp_path):
    log_path = tmp_path / "desktop.log"
    log_path.write_text("first line\nlatest line\n", encoding="utf-8")
    process = _ExitedProcess()
    report = launcher.diagnostic_report(process, log_path, 8765)
    assert "127.0.0.1:8765" in report
    assert "exited with code 2" in report
    assert "latest line" in report
    assert "CommLab version: 3.8.1" in report
    assert "Runtime mode: source" in report
    assert "Dashboard:" in report


def test_log_tail_reads_only_latest_text(tmp_path):
    log_path = tmp_path / "large.log"
    log_path.write_text("old\n" * 3000 + "latest unicode 中文\n", encoding="utf-8")
    tail = launcher.log_tail(log_path, limit=80)
    assert len(tail) <= 80
    assert tail.endswith("latest unicode 中文")


def test_log_tail_handles_missing_log(tmp_path):
    assert "Unable to read desktop log" in launcher.log_tail(tmp_path / "missing.log")
