"""Run the accepted curated Vehicle Engineering DB application locally.

This is the normal-use runner for the Windows launcher.  It intentionally does
not create, migrate, seed, rebuild, or replace a database.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


CURATED_DATABASE_NAME = "vehicle_engineering_curated.db"
CURATED_DATABASE_URL = f"sqlite:///./{CURATED_DATABASE_NAME}"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_READY_TIMEOUT_SECONDS = 30.0
START_PATH = "/"
READY_PATH = "/api/vehicles"


class LauncherError(RuntimeError):
    """An actionable preflight or launch error."""


@dataclass(frozen=True)
class HttpResult:
    status: int
    headers: dict[str, str]
    body: bytes


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        del req, fp, code, msg, headers, newurl
        return None


_HTTP_OPENER = urllib.request.build_opener(_NoRedirectHandler())
HttpGetter = Callable[[str, float], HttpResult | None]


def resolve_repository_root(script_file: Path | None = None) -> Path:
    """Resolve the repository from this script, independent of caller CWD."""

    script_path = Path(script_file or __file__).resolve()
    return script_path.parents[1]


def curated_database_path(repository_root: Path) -> Path:
    return Path(repository_root).resolve() / CURATED_DATABASE_NAME


def ensure_curated_database(database_path: Path) -> Path:
    """Require the accepted DB without creating or selecting another DB."""

    database_path = Path(database_path).resolve()
    if database_path.is_file():
        return database_path

    if database_path.exists():
        detail = "The path exists but is not a regular file."
    else:
        detail = "The file was not found."
    raise LauncherError(
        f"Accepted curated database is unavailable: {database_path}\n"
        f"{detail}\n\n"
        "Run the one-time controlled build from the repository root, then launch again:\n"
        "  python scripts/build_curated_db.py\n\n"
        "This launcher never creates, seeds, migrates, rebuilds, or replaces a database, "
        "and it will not fall back to vehicle_engineering.db."
    )


def read_curated_vehicle_codes(database_path: Path) -> frozenset[str] | None:
    """Read vehicle identities read-only for conservative running-app detection."""

    try:
        read_only_uri = f"{Path(database_path).resolve().as_uri()}?mode=ro"
        with sqlite3.connect(read_only_uri, uri=True) as connection:
            rows = connection.execute(
                "SELECT stable_vehicle_code FROM vehicle_configuration ORDER BY stable_vehicle_code"
            ).fetchall()
    except (OSError, sqlite3.Error):
        return None
    return frozenset(str(row[0]) for row in rows if row[0] is not None)


def validate_curated_database(database_path: Path) -> frozenset[str]:
    """Require a readable, non-empty curated dataset before importing the app."""

    codes = read_curated_vehicle_codes(database_path)
    if codes is None:
        raise LauncherError(
            f"Accepted curated database could not be read: {Path(database_path).resolve()}\n"
            "The file is not a readable initialized curated database. Run the controlled build "
            "from the repository root, then launch again."
        )
    if not codes:
        raise LauncherError(
            f"Accepted curated database contains no vehicle configurations: {Path(database_path).resolve()}\n"
            "Run the controlled build from the repository root, then launch again."
        )
    if any(code.startswith("FIXTURE-") for code in codes):
        raise LauncherError(
            f"Accepted curated database contains Phase 0 fixture identities: {Path(database_path).resolve()}\n"
            "Restore the accepted curated database or run the controlled curated build."
        )
    return codes


def prepare_runtime(repository_root: Path) -> Path:
    """Set the process CWD/import path and curated URL before app import."""

    repository_root = Path(repository_root).resolve()
    os.chdir(repository_root)
    os.environ["DATABASE_URL"] = CURATED_DATABASE_URL
    repository_root_text = str(repository_root)
    if repository_root_text not in sys.path:
        sys.path.insert(0, repository_root_text)
    return repository_root


def load_application(repository_root: Path):
    """Import the FastAPI app only after the curated runtime is prepared."""

    prepare_runtime(repository_root)
    from app.main import app

    return app


def local_url(host: str, port: int, path: str = START_PATH) -> str:
    """Build a browser URL for a local listener."""

    browser_host = "127.0.0.1" if host in {"", "0.0.0.0", "::"} else host
    normalized_path = "/" + path.lstrip("/")
    return f"http://{browser_host}:{port}{normalized_path}"


def port_is_available(host: str, port: int) -> bool:
    """Check bindability without inspecting or terminating another process."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind((host, port))
        except OSError:
            return False
    return True


def _http_get(url: str, timeout: float) -> HttpResult | None:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json, text/html;q=0.9, */*;q=0.1"},
        method="GET",
    )
    try:
        with _HTTP_OPENER.open(request, timeout=timeout) as response:
            return HttpResult(
                status=response.status,
                headers={str(key): str(value) for key, value in response.headers.items()},
                body=response.read(1_000_000),
            )
    except urllib.error.HTTPError as error:
        try:
            body = error.read(1_000_000)
        except OSError:
            body = b""
        return HttpResult(
            status=error.code,
            headers={str(key): str(value) for key, value in error.headers.items()},
            body=body,
        )
    except (OSError, urllib.error.URLError, ValueError):
        return None


def _header(headers: dict[str, str], name: str) -> str | None:
    wanted = name.lower()
    for key, value in headers.items():
        if key.lower() == wanted:
            return value
    return None


def _json_body(result: HttpResult) -> object | None:
    try:
        return json.loads(result.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def is_curated_app_running(
    base_url: str,
    expected_vehicle_codes: Iterable[str] | None = None,
    *,
    timeout: float = 0.8,
    http_get: HttpGetter | None = None,
) -> bool:
    """Recognize only the known app contract backed by the local curated set."""

    getter = http_get or _http_get
    base_url = base_url.rstrip("/")

    health = getter(f"{base_url}/healthz", timeout)
    if health is None or health.status != 200 or _json_body(health) != {"status": "ok"}:
        return False

    root = getter(f"{base_url}/", timeout)
    if root is None or root.status not in {307, 308}:
        return False
    location = _header(root.headers, "Location")
    parsed_location = urllib.parse.urlsplit(location or "")
    if (
        location is None
        or parsed_location.scheme
        or parsed_location.netloc
        or parsed_location.path.rstrip("/") != "/vehicles"
    ):
        return False

    if expected_vehicle_codes is None:
        return True

    vehicles = getter(f"{base_url}{READY_PATH}", timeout)
    if vehicles is None or vehicles.status != 200:
        return False
    payload = _json_body(vehicles)
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        return False
    items = payload["items"]
    if payload.get("count") != len(items):
        return False
    if any(not isinstance(item, dict) or "stable_vehicle_code" not in item for item in items):
        return False
    actual_codes = {str(item["stable_vehicle_code"]) for item in items}
    return actual_codes == set(expected_vehicle_codes)


def wait_for_server(
    url: str,
    *,
    timeout: float = DEFAULT_READY_TIMEOUT_SECONDS,
    http_get: HttpGetter | None = None,
    stop_event: threading.Event | None = None,
) -> bool:
    """Wait for a successful HTTP response without blocking shutdown for long."""

    getter = http_get or _http_get
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if stop_event is not None and stop_event.is_set():
            return False
        remaining = max(0.05, min(1.0, deadline - time.monotonic()))
        try:
            result = getter(url, remaining)
        except Exception:
            result = None
        if result is not None and 200 <= result.status < 400:
            return True
        if stop_event is not None and stop_event.wait(min(0.2, remaining)):
            return False
        time.sleep(0.05)
    return False


def open_browser_best_effort(url: str, browser_opener: Callable[[str], object] | None = None) -> bool:
    """Open a URL if possible; browser failures are warnings, never launch errors."""

    opener = browser_opener or webbrowser.open
    try:
        opened = bool(opener(url))
    except Exception as error:  # Browser integrations vary by Windows installation.
        print(f"Warning: could not open the browser automatically: {error}", file=sys.stderr)
        return False
    if not opened:
        print("Warning: the browser did not accept the automatic open request.", file=sys.stderr)
    return opened


def dependency_error_message(error: ModuleNotFoundError) -> str:
    missing_module = error.name or "a required application module"
    return (
        f"ERROR: required Python module '{missing_module}' is not installed.\n"
        "Install the project environment/dependencies once, then try again:\n"
        "  py -3.11 -m venv .venv\n"
        '  .venv\\Scripts\\python.exe -m pip install -e ".[dev]"\n\n'
        "No packages were installed automatically."
    )


def _open_browser_when_ready(
    browser_url: str,
    ready_url: str,
    ready_timeout: float,
    stop_event: threading.Event,
    browser_opener: Callable[[str], object] | None,
) -> None:
    if wait_for_server(ready_url, timeout=ready_timeout, stop_event=stop_event):
        if not stop_event.is_set():
            open_browser_best_effort(browser_url, browser_opener)
    elif not stop_event.is_set():
        print(
            f"Warning: the server did not answer {ready_url} within {ready_timeout:g} seconds; "
            "the browser was not opened automatically.",
            file=sys.stderr,
        )


def serve_application(
    application,
    *,
    host: str,
    port: int,
    browser_url: str,
    ready_url: str,
    open_browser: bool = True,
    ready_timeout: float = DEFAULT_READY_TIMEOUT_SECONDS,
    browser_opener: Callable[[str], object] | None = None,
    server_factory=None,
) -> int:
    """Run Uvicorn in-process and arrange a clean Ctrl+C/browser lifecycle."""

    import uvicorn

    config = uvicorn.Config(application, host=host, port=port, reload=False)
    server = (server_factory or uvicorn.Server)(config)
    stop_event = threading.Event()
    browser_thread: threading.Thread | None = None
    if open_browser:
        browser_thread = threading.Thread(
            target=_open_browser_when_ready,
            args=(browser_url, ready_url, ready_timeout, stop_event, browser_opener),
            name="vehicle-db-browser-opener",
            daemon=True,
        )
        browser_thread.start()

    try:
        server.run()
    except KeyboardInterrupt:
        server.should_exit = True
        print("Vehicle Engineering DB stopped.")
    finally:
        stop_event.set()
        if browser_thread is not None:
            browser_thread.join(timeout=1.0)
    return 0


def _port_number(value: str) -> int:
    try:
        port = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("port must be an integer") from error
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def _positive_seconds(value: str) -> float:
    try:
        seconds = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be a number") from error
    if seconds <= 0:
        raise argparse.ArgumentTypeError("timeout must be greater than zero")
    return seconds


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the curated Vehicle Engineering DB locally")
    parser.add_argument("--host", default=DEFAULT_HOST, help="local listen host (default: 127.0.0.1)")
    parser.add_argument("--port", type=_port_number, default=DEFAULT_PORT, help="listen port (default: 8000)")
    parser.add_argument(
        "--ready-timeout",
        type=_positive_seconds,
        default=DEFAULT_READY_TIMEOUT_SECONDS,
        help="seconds to wait before giving up on automatic browser opening",
    )
    parser.add_argument("--no-browser", action="store_true", help="do not open the default browser")
    return parser.parse_args(argv)


def run_local_app(
    *,
    repository_root: Path | None = None,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    open_browser: bool = True,
    ready_timeout: float = DEFAULT_READY_TIMEOUT_SECONDS,
) -> int:
    root = Path(repository_root).resolve() if repository_root is not None else resolve_repository_root()
    database_path = ensure_curated_database(curated_database_path(root))
    expected_codes = validate_curated_database(database_path)
    prepare_runtime(root)

    browser_url = local_url(host, port, START_PATH)
    if not port_is_available(host, port):
        if is_curated_app_running(browser_url, expected_codes):
            print(f"The curated Vehicle Engineering DB is already running at {browser_url}")
            if open_browser:
                open_browser_best_effort(browser_url)
            return 0
        raise LauncherError(
            f"Port {port} on {host} is already in use.\n"
            "The launcher did not stop or kill any process. Close the other application, "
            "or run this script with a different --port."
        )

    application = load_application(root)
    return serve_application(
        application,
        host=host,
        port=port,
        browser_url=browser_url,
        ready_url=local_url(host, port, READY_PATH),
        open_browser=open_browser,
        ready_timeout=ready_timeout,
    )


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return run_local_app(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
            ready_timeout=args.ready_timeout,
        )
    except ModuleNotFoundError as error:
        print(dependency_error_message(error), file=sys.stderr)
        return 1
    except LauncherError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"ERROR: could not start the local server: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
