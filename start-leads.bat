@echo off
cd /d "%~dp0"
echo Starting Voltaris Lead Manager with SQLite database...
py -3 server\app.py
if errorlevel 1 python server\app.py
pause
