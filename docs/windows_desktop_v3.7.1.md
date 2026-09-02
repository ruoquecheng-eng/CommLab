# CommLab v3.7.1 Windows Desktop

## 给普通用户

正式构建会提供两个文件：

- `CommLab-Setup-v3.7.1-Windows-x64.exe`：推荐使用的安装程序；
- `CommLab-Windows-x64.zip`：无需安装的便携版。

安装程序可在开始菜单创建 CommLab，并可选创建桌面快捷方式。双击后会出现一个小型控制窗口，后台启动本机 Streamlit 服务，并在默认浏览器打开完整 Dashboard。关闭控制窗口会同时停止后台服务。

所有仿真仍在本机运行，服务只监听 `127.0.0.1`，不会开放到局域网或互联网。首次启动可能需要十几秒。运行日志位于 `%LOCALAPPDATA%\CommLab\logs\desktop.log`。

当前安装程序没有商业代码签名证书。Windows SmartScreen 可能显示“未知发布者”；这不等于程序检测到病毒，但公开分发前仍建议购买代码签名证书并在干净 Windows 虚拟机复验。

## 开发者本地运行

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[desktop]"
python desktop\launcher.py
```

无界面烟雾测试：

```powershell
python desktop\launcher.py --smoke-test
```

## 构建 Windows 安装包

```powershell
powershell -ExecutionPolicy Bypass -File desktop\build_windows.ps1
```

脚本使用 PyInstaller onedir 构建。若系统已安装 Inno Setup，还会同时生成安装器。GitHub Actions 的 `Build Windows Desktop` workflow 会在 `windows-latest` 上执行同一类构建并上传两个 artifacts。

## 技术边界

桌面版是本地启动外壳，不是对 Dashboard 的第二套重写。浏览器仍是 Streamlit 前端，Python 子进程是本机服务端。这与 Streamlit 官方描述的客户端—服务端结构一致，也避免复制一百多个实验界面。
