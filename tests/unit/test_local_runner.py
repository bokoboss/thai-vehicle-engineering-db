from __future__ import annotations

import ast
import json
import os
import sqlite3
import sys
import urllib.parse
from pathlib import Path

import pytest

from scripts import run_local_app


def test_missing_curated_database_refuses_safely(tmp_path: Path):
    database_path = tmp_path / run_local_app.CURATED_DATABASE_NAME

    with pytest.raises(run_local_app.LauncherError) as error:
        run_local_app.ensure_curated_database(database_path)

    message = str(error.value)
    assert str(database_path) in message
    assert "build_curated_db.py" in message
    assert "vehicle_engineering.db" in message


def test_runtime_preparation_sets_curated_url_and_cwd(monkeypatch, tmp_path: Path):
    repository_root = tmp_path / "repository"
    repository_root.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./vehicle_engineering.db")

    repository_root_text = str(repository_root.resolve())
    try:
        assert run_local_app.prepare_runtime(repository_root) == repository_root.resolve()
        assert Path.cwd() == repository_root.resolve()
        assert os.environ["DATABASE_URL"] == run_local_app.CURATED_DATABASE_URL
        assert sys.path[0] == repository_root_text
    finally:
        if repository_root_text in sys.path:
            sys.path.remove(repository_root_text)


def test_run_local_app_forces_curated_environment_before_app_import(monkeypatch, tmp_path: Path):
    repository_root = tmp_path / "repository"
    repository_root.mkdir()
    database_path = repository_root / run_local_app.CURATED_DATABASE_NAME
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE vehicle_configuration (stable_vehicle_code TEXT NOT NULL)")
        connection.execute("INSERT INTO vehicle_configuration VALUES (?)", ("TH-ATTO3",))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./vehicle_engineering.db")
    monkeypatch.setattr(run_local_app, "port_is_available", lambda host, port: True)
    monkeypatch.setattr(run_local_app, "load_application", lambda root: object())
    captured = {}

    def fake_serve(application, **kwargs):
        captured["application"] = application
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(run_local_app, "serve_application", fake_serve)
    repository_root_text = str(repository_root.resolve())
    try:
        assert run_local_app.run_local_app(repository_root=repository_root, open_browser=False) == 0
        assert os.environ["DATABASE_URL"] == run_local_app.CURATED_DATABASE_URL
        assert Path.cwd() == repository_root.resolve()
        assert captured["ready_url"] == "http://127.0.0.1:8000/api/vehicles"
    finally:
        if repository_root_text in sys.path:
            sys.path.remove(repository_root_text)


def test_repository_root_resolution_does_not_depend_on_caller_cwd(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)

    script_path = Path(run_local_app.__file__).resolve()

    assert run_local_app.resolve_repository_root() == script_path.parents[1]


def test_local_urls_use_root_start_page_and_api_readiness_path():
    assert run_local_app.local_url("127.0.0.1", 8000) == "http://127.0.0.1:8000/"
    assert run_local_app.local_url("127.0.0.1", 8000, run_local_app.READY_PATH) == (
        "http://127.0.0.1:8000/api/vehicles"
    )


def test_curated_app_detection_requires_health_redirect_and_curated_vehicle_set():
    base_url = "http://127.0.0.1:8000/"
    expected_codes = {"TH-ATTO3", "TH-CIVIC"}
    responses = {
        "/healthz": run_local_app.HttpResult(200, {}, b'{"status":"ok"}'),
        "/": run_local_app.HttpResult(307, {"Location": "/vehicles"}, b""),
        "/api/vehicles": run_local_app.HttpResult(
            200,
            {},
            json.dumps(
                {
                    "count": 2,
                    "items": [{"stable_vehicle_code": code} for code in sorted(expected_codes)],
                }
            ).encode(),
        ),
    }

    def fake_http_get(url: str, timeout: float):
        del timeout
        return responses[urllib.parse.urlsplit(url).path]

    assert run_local_app.is_curated_app_running(
        base_url,
        expected_codes,
        http_get=fake_http_get,
    )

    responses["/api/vehicles"] = run_local_app.HttpResult(
        200,
        {},
        b'{"count":1,"items":[{"stable_vehicle_code":"FIXTURE-ONLY"}]}',
    )
    assert not run_local_app.is_curated_app_running(
        base_url,
        expected_codes,
        http_get=fake_http_get,
    )


def test_curated_database_validation_rejects_phase0_fixture_rows(tmp_path: Path):
    database_path = tmp_path / run_local_app.CURATED_DATABASE_NAME
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE vehicle_configuration (stable_vehicle_code TEXT NOT NULL)")
        connection.execute("INSERT INTO vehicle_configuration VALUES (?)", ("FIXTURE-SYNTHETIC",))

    with pytest.raises(run_local_app.LauncherError, match="Phase 0 fixture"):
        run_local_app.validate_curated_database(database_path)


def test_browser_open_failure_is_best_effort(capsys):
    assert not run_local_app.open_browser_best_effort("http://127.0.0.1:8000/", lambda url: False)
    assert "did not accept" in capsys.readouterr().err


def test_missing_dependency_returns_nonzero_with_actionable_setup_message(monkeypatch, capsys):
    missing = ModuleNotFoundError("No module named 'fastapi'", name="fastapi")

    def fail_to_load(**kwargs):
        del kwargs
        raise missing

    monkeypatch.setattr(run_local_app, "run_local_app", fail_to_load)

    assert run_local_app.main(["--no-browser"]) == 1
    error = capsys.readouterr().err
    assert "fastapi" in error
    assert "py -3.11 -m venv .venv" in error
    assert '.venv\\Scripts\\python.exe -m pip install -e ".[dev]"' in error
    assert "No packages were installed automatically" in error
    assert "Traceback" not in error


def test_missing_dependency_handling_has_no_automatic_setup_calls():
    repository_root = Path(run_local_app.__file__).resolve().parents[1]
    source = (repository_root / "scripts" / "run_local_app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    called_functions = {ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)}

    assert "subprocess" not in source
    assert "os.system" not in source
    assert not any(
        function in {"subprocess.run", "subprocess.call", "subprocess.Popen", "os.system", "os.startfile"}
        for function in called_functions
    )


def test_server_configuration_disables_reload_and_opens_after_readiness(monkeypatch):
    opened: list[str] = []
    captured = {}

    class FakeServer:
        should_exit = False

        def run(self):
            captured["ran"] = True

    def fake_server_factory(config):
        captured["reload"] = config.reload
        return FakeServer()

    monkeypatch.setattr(run_local_app, "wait_for_server", lambda *args, **kwargs: True)

    assert run_local_app.serve_application(
        object(),
        host="127.0.0.1",
        port=8000,
        browser_url="http://127.0.0.1:8000/",
        ready_url="http://127.0.0.1:8000/api/vehicles",
        browser_opener=lambda url: opened.append(url) or True,
        server_factory=fake_server_factory,
    ) == 0
    assert captured == {"reload": False, "ran": True}
    assert opened == ["http://127.0.0.1:8000/"]


def test_launcher_files_do_not_invoke_phase0_seeder():
    repository_root = Path(run_local_app.__file__).resolve().parents[1]
    runner_text = (repository_root / "scripts" / "run_local_app.py").read_text(encoding="utf-8")
    launcher_text = (repository_root / "Start Vehicle Engineering DB.cmd").read_text(encoding="utf-8")

    assert "app.seed" not in runner_text
    assert "app.seed" not in launcher_text
    assert "python -m alembic" not in launcher_text
    assert "build_wave1_curated_db.py" not in launcher_text


def test_windows_launcher_is_repository_relative_and_prefers_venv():
    repository_root = Path(run_local_app.__file__).resolve().parents[1]
    launcher_text = (repository_root / "Start Vehicle Engineering DB.cmd").read_text(encoding="utf-8")

    assert 'cd /d "%~dp0"' in launcher_text
    assert "%~dp0.venv\\Scripts\\python.exe" in launcher_text
    assert "%~dp0scripts\\run_local_app.py" in launcher_text
    assert "py -3" in launcher_text
    assert "python" in launcher_text
    assert "pause" in launcher_text
