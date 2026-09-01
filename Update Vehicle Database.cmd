@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "BUILDER=%~dp0scripts\build_curated_db.py"
set "RELEASE=%~dp0data\curation\releases\release_2026_09_a.json"
set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
set "EXIT_CODE=1"

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
    if not errorlevel 1 goto :run_venv
)

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
    if not errorlevel 1 goto :run_py_launcher
)

where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
    if not errorlevel 1 goto :run_python
)

echo Could not find Python 3.11 or newer.
echo Install Python 3.11+ or create the repository .venv, then try again.
goto :failed

:run_venv
"%VENV_PYTHON%" "%BUILDER%" --release "%RELEASE%" --replace-final
set "EXIT_CODE=%ERRORLEVEL%"
goto :finish

:run_py_launcher
py -3 "%BUILDER%" --release "%RELEASE%" --replace-final
set "EXIT_CODE=%ERRORLEVEL%"
goto :finish

:run_python
python "%BUILDER%" --release "%RELEASE%" --replace-final
set "EXIT_CODE=%ERRORLEVEL%"
goto :finish

:failed
set "EXIT_CODE=1"

:finish
if not "%EXIT_CODE%"=="0" (
    echo.
    echo Vehicle database update failed. The previous accepted database was not replaced.
    pause
)
endlocal & exit /b %EXIT_CODE%
