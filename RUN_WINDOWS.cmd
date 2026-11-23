@echo off
setlocal
cd /d "%~dp0"
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if not errorlevel 1 goto use_py
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 goto no_python
python -B verify.py
goto finished
:use_py
py -3 -B verify.py
:finished
set "verify_exit=%errorlevel%"
echo.
if "%verify_exit%"=="0" (
    echo Verification passed. Open reports\latest.json for the report location.
) else (
    echo Verification did not pass. Read the error above. Python 3.8 or later is required.
)
pause
exit /b %verify_exit%
:no_python
echo Python 3.8 or later was not found. Install Python and enable its PATH option.
pause
exit /b 1
