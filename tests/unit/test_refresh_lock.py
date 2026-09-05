from __future__ import annotations

import multiprocessing
import os
from pathlib import Path

import pytest

from scripts import build_curated_db as builder


def _hold_refresh_lock(
    database_path: str,
    entered,
    release,
    active,
) -> None:
    with builder.database_refresh_lock(Path(database_path), timeout_seconds=5):
        with active.get_lock():
            if active.value:
                os._exit(2)
            active.value += 1
        entered.set()
        release.wait(5)
        with active.get_lock():
            active.value -= 1


def _crash_with_refresh_lock(database_path: str, entered) -> None:
    with builder.database_refresh_lock(Path(database_path), timeout_seconds=5):
        entered.set()
        os._exit(0)


def _join_processes(*processes) -> None:
    for process in processes:
        process.join(5)
        if process.is_alive():
            process.terminate()
            process.join(5)


def test_cross_process_refresh_lock_serializes_shared_promotion(tmp_path: Path):
    database = tmp_path / "vehicle_engineering_curated.db"
    context = multiprocessing.get_context("spawn")
    owner_entered = context.Event()
    contender_entered = context.Event()
    release_owner = context.Event()
    release_contender = context.Event()
    active = context.Value("i", 0)
    owner = context.Process(
        target=_hold_refresh_lock,
        args=(str(database), owner_entered, release_owner, active),
    )
    contender = context.Process(
        target=_hold_refresh_lock,
        args=(str(database), contender_entered, release_contender, active),
    )

    owner.start()
    contender_started = False
    try:
        assert owner_entered.wait(5)
        contender.start()
        contender_started = True
        assert not contender_entered.wait(0.3)
        release_owner.set()
        assert contender_entered.wait(5)
        release_contender.set()
    finally:
        release_owner.set()
        release_contender.set()
        _join_processes(owner, contender)

    assert owner.exitcode == 0
    if contender_started:
        assert contender.exitcode == 0
    assert active.value == 0


def test_refresh_lock_releases_on_context_exit_and_process_crash(tmp_path: Path):
    database = tmp_path / "vehicle_engineering_curated.db"

    with pytest.raises(RuntimeError, match="injected lock-body failure"):
        with builder.database_refresh_lock(database, timeout_seconds=1):
            raise RuntimeError("injected lock-body failure")
    with builder.database_refresh_lock(database, timeout_seconds=1):
        pass

    context = multiprocessing.get_context("spawn")
    crashed_entered = context.Event()
    crashed = context.Process(
        target=_crash_with_refresh_lock,
        args=(str(database), crashed_entered),
    )
    crashed.start()
    crashed.join(5)
    if crashed.is_alive():
        crashed.terminate()
        crashed.join(5)
    assert crashed.exitcode == 0
    assert crashed_entered.is_set()

    with builder.database_refresh_lock(database, timeout_seconds=1):
        pass
