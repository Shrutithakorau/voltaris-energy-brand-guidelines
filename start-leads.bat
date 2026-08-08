@echo off
cd /d "%~dp0"
echo Starting local static server for Voltaris Lead Manager...
echo Make sure js\supabase-config.js has your Supabase URL + anon key.
echo.
echo Opening http://127.0.0.1:8787/leads.html
echo Keep this window open.
echo.
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8787 ^| findstr LISTENING') do (
  taskkill /F /PID %%a >nul 2>&1
)
start "" "http://127.0.0.1:8787/leads.html"
py -3 -m http.server 8787 --bind 127.0.0.1
if errorlevel 1 python -m http.server 8787 --bind 127.0.0.1
pause
