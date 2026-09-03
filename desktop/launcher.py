from __future__ import annotations

import argparse
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from typing import Callable
import urllib.request
import webbrowser


APP_VERSION = "3.7.1"
HEALTH_PATH = "/_stcore/health"


def resource_root() -> Path:
    """Return the source root or PyInstaller extraction root."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")).resolve()
    return Path(__file__).resolve().parents[1]


def dashboard_path(root: Path | None = None) -> Path:
    return (root or resource_root()) / "app" / "dashboard.py"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def streamlit_flags(port: int) -> dict[str, object]:
    return {
        "global.developmentMode": False,
        "server.address": "127.0.0.1",
        "server.port": int(port),
        "server.headless": True,
        "server.fileWatcherType": "none",
        "browser.gatherUsageStats": False,
        "client.showErrorDetails": "full",
    }


def server_command(port: int) -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--server-child", str(port)]
    return [sys.executable, str(Path(__file__).resolve()), "--server-child", str(port)]


def user_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_STATE_HOME")
    if not base:
        base = str(Path.home() / ".local" / "state")
    path = Path(base) / "CommLab"
    path.mkdir(parents=True, exist_ok=True)
    return path


def configure_child_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    cache = user_data_dir() / "cache" / "matplotlib"
    cache.mkdir(parents=True, exist_ok=True)
    env["MPLCONFIGDIR"] = str(cache)
    return env


def start_server(port: int) -> tuple[subprocess.Popen, Path]:
    log_dir = user_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "desktop.log"
    log_handle = log_path.open("a", encoding="utf-8")
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    process = subprocess.Popen(
        server_command(port),
        cwd=resource_root(),
        env=configure_child_environment(),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        creationflags=creationflags,
    )
    log_handle.close()
    return process, log_path


def log_tail(log_path: Path, limit: int = 2400) -> str:
    """Read the newest launcher output without failing the UI on I/O errors."""
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"Unable to read desktop log: {exc}"
    return text[-limit:].strip() or "No launcher output was recorded."


def diagnostic_report(process: subprocess.Popen | None, log_path: Path, port: int) -> str:
    """Produce a compact, copyable failure report for the desktop window."""
    exit_code = None if process is None else process.poll()
    state = "still running" if exit_code is None else f"exited with code {exit_code}"
    return (
        f"Local address: http://127.0.0.1:{port}\n"
        f"Server state: {state}\n"
        f"Log file: {log_path}\n\n"
        f"Latest log output:\n{log_tail(log_path)}"
    )


def open_log_file(log_path: Path) -> None:
    """Open the log with the platform default application when available."""
    if sys.platform.startswith("win") and hasattr(os, "startfile"):
        os.startfile(str(log_path))  # type: ignore[attr-defined]
    else:
        webbrowser.open(log_path.resolve().as_uri())


def wait_until_ready(
    process: subprocess.Popen,
    port: int,
    timeout: float = 45.0,
    opener: Callable = urllib.request.urlopen,
) -> bool:
    deadline = time.monotonic() + timeout
    url = f"http://127.0.0.1:{port}{HEALTH_PATH}"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with opener(url, timeout=.7) as response:
                if getattr(response, "status", 200) == 200:
                    return True
        except Exception:
            time.sleep(.12)
    return False


def stop_server(process: subprocess.Popen | None, timeout: float = 5.0) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=timeout)


def run_streamlit_server(port: int) -> int:
    script = dashboard_path()
    if not script.exists():
        raise FileNotFoundError(f"CommLab Dashboard is missing: {script}")
    os.chdir(resource_root())
    from streamlit.web import bootstrap
    flags=streamlit_flags(port)
    bootstrap.load_config_options(flags)
    bootstrap.run(str(script), False, [], flags)
    return 0


def run_smoke_test() -> int:
    port = find_free_port()
    process, log_path = start_server(port)
    try:
        if not wait_until_ready(process, port):
            print(f"desktop smoke test failed; log={log_path}", file=sys.stderr)
            return 1
        print(f"desktop smoke test OK: http://127.0.0.1:{port}")
        return 0
    finally:
        stop_server(process)


def run_gui() -> int:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title(f"CommLab {APP_VERSION} Desktop")
    root.geometry("575x315")
    root.resizable(False, False)
    state: dict[str, object] = {"process": None, "log_path": None, "port": None, "ready": False}

    title = tk.Label(root, text="CommLab Desktop", font=("Segoe UI", 22, "bold"))
    title.pack(pady=(24, 6))
    subtitle = tk.Label(root, text="无线通信 · 边缘智能 · 可靠性编排实验平台", font=("Microsoft YaHei UI", 10))
    subtitle.pack()
    status_var = tk.StringVar(value="正在启动本地仿真服务……")
    status = tk.Label(root, textvariable=status_var, font=("Microsoft YaHei UI", 10), fg="#555555")
    status.pack(pady=(25, 12))
    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)
    open_button = tk.Button(button_frame, text="打开 CommLab", width=17, state="disabled")
    open_button.grid(row=0, column=0, padx=6)

    def copy_address() -> None:
        port = state.get("port")
        if port is None:
            return
        root.clipboard_clear(); root.clipboard_append(f"http://127.0.0.1:{port}"); root.update()

    copy_button = tk.Button(button_frame, text="复制本地地址", width=17, command=copy_address)
    copy_button.grid(row=0, column=1, padx=6)
    log_button = tk.Button(button_frame, text="打开启动日志", width=17, state="disabled")
    log_button.grid(row=0, column=2, padx=6)
    retry_button = tk.Button(root, text="重新启动服务", width=17)
    retry_button.pack(pady=(12, 0))
    hint = tk.Label(root, text="此窗口负责后台服务；关闭窗口即退出 CommLab。所有计算仅在本机运行。",
                    font=("Microsoft YaHei UI", 9), fg="#777777")
    hint.pack(pady=(20, 0))

    def apply_startup_result(ready: bool) -> None:
        process = state.get("process")
        log_path = state.get("log_path")
        port = state.get("port")
        assert isinstance(log_path, Path) and isinstance(port, int)
        if ready:
            url = f"http://127.0.0.1:{port}"
            state["ready"] = True
            status_var.set(f"运行中 · {url}")
            status.configure(fg="#19723b")
            open_button.configure(state="normal")
            log_button.configure(state="normal")
            open_button.configure(command=lambda: webbrowser.open(url))
            log_button.configure(command=lambda: open_log_file(log_path))
            webbrowser.open(url)
            root.after(1200, monitor_server)
        else:
            state["ready"] = False
            status_var.set("启动失败")
            status.configure(fg="#a12622")
            log_button.configure(state="normal", command=lambda: open_log_file(log_path))
            messagebox.showerror("CommLab 启动失败", diagnostic_report(process, log_path, port))

    def finish_startup() -> None:
        process = state.get("process")
        port = state.get("port")
        assert process is not None and isinstance(port, int)
        ready=wait_until_ready(process, port)
        root.after(0, lambda: apply_startup_result(ready))

    def begin_startup() -> None:
        port = find_free_port()
        process, log_path = start_server(port)
        state.update(process=process, log_path=log_path, port=port, ready=False)
        status_var.set("正在启动本地仿真服务……")
        status.configure(fg="#555555")
        open_button.configure(state="disabled")
        log_button.configure(state="normal", command=lambda: open_log_file(log_path))
        threading.Thread(target=finish_startup, daemon=True).start()

    def restart_server() -> None:
        previous = state.get("process")
        if previous is not None:
            stop_server(previous)  # type: ignore[arg-type]
        begin_startup()

    def monitor_server() -> None:
        process = state.get("process")
        if process is not None and process.poll() is not None:
            state["ready"] = False
            status_var.set("后台服务已退出；可点击“重新启动服务”")
            status.configure(fg="#a12622")
            open_button.configure(state="disabled")
            return
        root.after(1200, monitor_server)

    def on_close() -> None:
        process = state.get("process")
        if process is not None:
            stop_server(process)  # type: ignore[arg-type]
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    retry_button.configure(command=restart_server)
    begin_startup()
    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CommLab Desktop launcher")
    parser.add_argument("--server-child", type=int, metavar="PORT")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args(argv)
    if args.server_child is not None:
        return run_streamlit_server(args.server_child)
    if args.smoke_test:
        return run_smoke_test()
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
