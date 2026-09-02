from pathlib import Path
import subprocess

from desktop import launcher


def test_source_resource_root_contains_dashboard():
    root=launcher.resource_root()
    assert (root/"app"/"dashboard.py").exists()


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
