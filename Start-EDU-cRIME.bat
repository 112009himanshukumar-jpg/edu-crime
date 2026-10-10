@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo EDU-cRIME has not been set up yet.
  echo First run SETUP-EDU-cRIME.bat and follow the instructions.
  pause
  exit /b 1
)
start "" cmd /c "timeout /t 2 /nobreak ^>nul ^& start http://127.0.0.1:5000"
".venv\Scripts\python.exe" app.py
pause
