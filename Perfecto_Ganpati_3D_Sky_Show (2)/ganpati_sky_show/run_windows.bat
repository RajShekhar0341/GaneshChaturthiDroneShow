@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe main.py
if errorlevel 1 goto fail
exit /b 0
:fail
echo Please install Python 3.11 or 3.12 from python.org and try again.
pause
