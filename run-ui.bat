@echo off
REM Run AI Agent as a native window (not a browser)
cd /d "%~dp0"
REM กัน 'charmap' codec บน Windows ภาษาไทย (เกราะชั้น launcher)
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
echo Checking / installing libraries...
py -m pip install --quiet -r requirements.txt
echo Opening AI Agent...
py server.py
pause
