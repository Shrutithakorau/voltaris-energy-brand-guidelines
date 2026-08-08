@echo off
cd /d "%~dp0"
echo Starting Voltaris Lead Manager...
echo.
echo IMPORTANT: Keep this window open.
echo Open this URL only: http://127.0.0.1:8787/leads.html
echo Do NOT open leads.html by double-clicking the file.
echo.

REM free port if old process stuck (best effort)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8787 ^| findstr LISTENING') do (
  taskkill /F /PID %%a >nul 2>&1
)

start "" "http://127.0.0.1:8787/leads.html"
py -3 -u server\app.py
if errorlevel 1 python -u server\app.py
echo.
echo Server stopped.
pause
