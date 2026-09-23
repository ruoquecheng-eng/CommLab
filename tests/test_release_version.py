from commlab import __version__

from app.run_record import make_record
from desktop.launcher import APP_VERSION


def test_release_version_matches_run_record_and_desktop_app():
    record = make_record("OFDM Link", 2026, {}, [], 0.1, __version__)
    assert record["version"] == "3.8.0"
    assert APP_VERSION == record["version"]
