@echo off
REM ------------------------------------------------
REM 1.  Create/activate a virtualenv in ".venv"
REM ------------------------------------------------
if not exist ".venv" (
    echo [+] Creating venv...
    python -m venv .venv
)
call .venv\Scripts\activate

REM ------------------------------------------------
REM 2.  Install / update required Python packages
REM ------------------------------------------------
echo [+] Installing Python deps...
pip install --upgrade -r "%~dp0..\requirements.txt"

REM ------------------------------------------------
REM 3.  Prepend Instant Client to PATH for this session
REM     (so oci.dll is found without system-wide edits)
REM ------------------------------------------------
set "PATH=%~dp0..\instantclient_23_8;%PATH%"

REM ------------------------------------------------
REM 4.  Launch the GUI
REM ------------------------------------------------
echo [+] Launching database GUI...
python "%~dp0..\src\dbgui.py"
pause
