from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from scripts import run_local_app


def _state(*codes: str) -> run_local_app.CurrentReleaseState:
    return run_local_app.CurrentReleaseState(
        release_id="current-test-release",
        release_definition="data/curation/releases/release_current.json",
        build_input_digest_sha256="current-build-input",
        stable_vehicle_digest_sha256="current-stable-digest",
        vehicle_count=len(codes),
        stable_vehicle_codes=frozenset(codes),
    )


def _write_database(path: Path, *codes: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE vehicle_configuration (stable_vehicle_code TEXT NOT NULL)")
        connection.executemany(
            "INSERT INTO vehicle_configuration VALUES (?)",
            [(code,) for code in codes],
        )


def _patch_launch(monkeypatch: pytest.MonkeyPatch, *, state, status, refresh=None):
    monkeypatch.setattr(run_local_app, "current_release_state", lambda root: state)
    monkeypatch.setattr(run_local_app, "database_matches_current_release", lambda path, current: status())
    monkeypatch.setattr(run_local_app, "port_is_available", lambda host, port: True)
    if refresh is not None:
        monkeypatch.setattr(
            run_local_app,
            "refresh_curated_database",
            lambda path, **kwargs: refresh(path),
        )


def test_matching_release_starts_without_invoking_builder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    database = root / run_local_app.CURATED_DATABASE_NAME
    _write_database(database, "TH-CURRENT")
    refresh_calls: list[Path] = []
    _patch_launch(
        monkeypatch,
        state=_state("TH-CURRENT"),
        status=lambda: (True, ""),
        refresh=lambda path: refresh_calls.append(path),
    )
    monkeypatch.setattr(run_local_app, "load_application", lambda repository_root: object())
    monkeypatch.setattr(run_local_app, "serve_application", lambda application, **kwargs: 0)

    assert run_local_app.run_local_app(repository_root=root, open_browser=False) == 0
    assert refresh_calls == []


def test_stale_release_invokes_builder_once_and_launches_refreshed_db(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    root = tmp_path / "repo"
    root.mkdir()
    _write_database(root / run_local_app.CURATED_DATABASE_NAME, "TH-CURRENT")
    statuses = iter(
        [
            (False, "build-input fingerprint is stale"),
            (False, "build-input fingerprint is still stale"),
            (True, ""),
        ]
    )
    refresh_calls: list[Path] = []
    _patch_launch(
        monkeypatch,
        state=_state("TH-CURRENT"),
        status=lambda: next(statuses),
        refresh=lambda path: refresh_calls.append(path),
    )
    captured: dict[str, object] = {}
    monkeypatch.setattr(run_local_app, "load_application", lambda repository_root: "refreshed-app")
    monkeypatch.setattr(
        run_local_app,
        "serve_application",
        lambda application, **kwargs: captured.update(application=application, **kwargs) or 0,
    )

    assert run_local_app.run_local_app(repository_root=root, open_browser=False) == 0
    assert len(refresh_calls) == 1
    assert captured["application"] == "refreshed-app"


def test_stale_release_recheck_skips_refresh_after_another_launcher_promotes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    root = tmp_path / "repo"
    root.mkdir()
    _write_database(root / run_local_app.CURATED_DATABASE_NAME, "TH-CURRENT")
    statuses = iter([(False, "build-input fingerprint is stale"), (True, "")])
    refresh_calls: list[Path] = []
    _patch_launch(
        monkeypatch,
        state=_state("TH-CURRENT"),
        status=lambda: next(statuses),
        refresh=lambda path: refresh_calls.append(path),
    )
    monkeypatch.setattr(run_local_app, "load_application", lambda repository_root: "refreshed-app")
    monkeypatch.setattr(run_local_app, "serve_application", lambda application, **kwargs: 0)

    assert run_local_app.run_local_app(repository_root=root, open_browser=False) == 0
    assert refresh_calls == []
    assert "Another launcher refreshed" in capsys.readouterr().out


def test_refresh_failure_warns_and_launches_previous_accepted_db(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    root = tmp_path / "repo"
    root.mkdir()
    final = root / run_local_app.CURATED_DATABASE_NAME
    _write_database(final, "TH-OLD")
    _patch_launch(
        monkeypatch,
        state=_state("TH-CURRENT"),
        status=lambda: (False, "current fingerprint is stale"),
        refresh=lambda path: (_ for _ in ()).throw(RuntimeError("candidate QA failed")),
    )
    captured: dict[str, object] = {}
    monkeypatch.setattr(run_local_app, "load_application", lambda repository_root: "old-app")
    monkeypatch.setattr(
        run_local_app,
        "serve_application",
        lambda application, **kwargs: captured.update(application=application, **kwargs) or 0,
    )

    assert run_local_app.run_local_app(repository_root=root, open_browser=False) == 0
    assert captured["application"] == "old-app"
    warning = capsys.readouterr().err
    assert "previous accepted local database" in warning
    assert "does not match" in warning
    assert "candidate QA failed" in warning


def test_refresh_failure_uses_previous_slot_when_current_db_is_unreadable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    root = tmp_path / "repo"
    root.mkdir()
    final = root / run_local_app.CURATED_DATABASE_NAME
    final.write_bytes(b"not sqlite")
    previous = final.with_name(final.name + ".previous")
    _write_database(previous, "TH-OLD")
    _patch_launch(
        monkeypatch,
        state=_state("TH-CURRENT"),
        status=lambda: (False, "current database is missing or stale"),
        refresh=lambda path: (_ for _ in ()).throw(RuntimeError("build failed")),
    )
    captured: dict[str, object] = {}

    def fake_load(repository_root, database_path=None):
        captured["database_path"] = database_path
        return "old-app"

    monkeypatch.setattr(run_local_app, "load_application", fake_load)
    monkeypatch.setattr(run_local_app, "serve_application", lambda application, **kwargs: 0)

    assert run_local_app.run_local_app(repository_root=root, open_browser=False) == 0
    assert captured["database_path"] == previous.resolve()


def test_refresh_failure_without_usable_db_fails_clearly(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    root = tmp_path / "repo"
    root.mkdir()
    _patch_launch(
        monkeypatch,
        state=_state("TH-CURRENT"),
        status=lambda: (False, "database is missing"),
        refresh=lambda path: (_ for _ in ()).throw(RuntimeError("build failed")),
    )

    with pytest.raises(run_local_app.LauncherError, match="no usable accepted local database"):
        run_local_app.run_local_app(repository_root=root, open_browser=False)


def test_no_auto_refresh_never_invokes_builder_and_launches_existing_db(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    root = tmp_path / "repo"
    root.mkdir()
    _write_database(root / run_local_app.CURATED_DATABASE_NAME, "TH-OLD")
    _patch_launch(
        monkeypatch,
        state=_state("TH-CURRENT"),
        status=lambda: (False, "fingerprint is stale"),
        refresh=lambda path: pytest.fail("builder must not be invoked"),
    )
    monkeypatch.setattr(run_local_app, "load_application", lambda repository_root: "old-app")
    monkeypatch.setattr(run_local_app, "serve_application", lambda application, **kwargs: 0)

    assert run_local_app.run_local_app(
        repository_root=root,
        open_browser=False,
        no_auto_refresh=True,
    ) == 0
    assert "automatic refresh is disabled" in capsys.readouterr().err


def test_running_app_port_safety_prevents_refresh_or_replacement(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    root = tmp_path / "repo"
    root.mkdir()
    _write_database(root / run_local_app.CURATED_DATABASE_NAME, "TH-CURRENT")
    refresh_calls: list[Path] = []
    _patch_launch(
        monkeypatch,
        state=_state("TH-CURRENT"),
        status=lambda: pytest.fail("database freshness must not replace a running app"),
        refresh=lambda path: refresh_calls.append(path),
    )
    monkeypatch.setattr(run_local_app, "port_is_available", lambda host, port: False)
    monkeypatch.setattr(run_local_app, "is_curated_app_running", lambda url, codes: True)
    monkeypatch.setattr(run_local_app, "open_browser_best_effort", lambda url: True)

    assert run_local_app.run_local_app(repository_root=root, open_browser=True) == 0
    assert refresh_calls == []


def test_no_auto_refresh_argument_is_parsed():
    assert run_local_app.parse_args(["--no-auto-refresh"]).no_auto_refresh is True
