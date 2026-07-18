@echo off
setlocal
cd /d "%~dp0"

echo ===============================================
echo  AI Phishing Email Detection - Quick Start
echo ===============================================

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating Python virtual environment...
  python -m venv .venv
  if errorlevel 1 goto :error
) else (
  echo [1/4] Virtual environment already exists.
)

echo [2/4] Installing project requirements...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto :error

echo [3/4] Training the demonstration model...
python scripts\train_model.py
if errorlevel 1 goto :error

echo [4/4] Starting the application...
echo Dashboard: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
start "" "http://127.0.0.1:8000"
python -m uvicorn app.main:app --reload
exit /b 0

:error
echo.
echo Setup failed. Review the error above.
pause
exit /b 1
