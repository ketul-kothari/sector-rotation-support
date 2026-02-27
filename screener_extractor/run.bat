@echo off
setlocal

:: ─── Config ───────────────────────────────────────────────────────────────────
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%VENV_DIR%\Scripts\pip.exe"

echo ============================================================
echo  NSE Screener Extractor
echo ============================================================
echo.

:: ─── Virtual environment ──────────────────────────────────────────────────────
if exist "%VENV_PYTHON%" (
    echo [INFO] Virtual environment found at %VENV_DIR%
) else (
    echo [INFO] Virtual environment not found. Creating at %VENV_DIR% ...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Make sure Python is installed and on PATH.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created.
)

:: ─── Install / update dependencies ───────────────────────────────────────────
echo.
echo [INFO] Installing / verifying dependencies from requirements.txt ...
"%VENV_PIP%" install -q -r "%SCRIPT_DIR%requirements.txt"
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)
echo [INFO] Dependencies ready.

:: ─── Step 1: Extract industry classification from PDF ─────────────────────────
echo.
echo [STEP 1] Extracting NSE industry classification from PDF ...
echo ─────────────────────────────────────────────────────────────
"%VENV_PYTHON%" "%SCRIPT_DIR%extract_industry_classification.py"
if errorlevel 1 (
    echo [ERROR] extract_industry_classification.py failed.
    pause
    exit /b 1
)

:: ─── Step 2: Scrape screener.in ───────────────────────────────────────────────
echo.
echo [STEP 2] Scraping screener.in for all basic industries ...
echo ─────────────────────────────────────────────────────────────
"%VENV_PYTHON%" "%SCRIPT_DIR%scrape_screener.py"
if errorlevel 1 (
    echo [ERROR] scrape_screener.py failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  All done! Output files are in:
echo  %SCRIPT_DIR%data\
echo ============================================================
pause
