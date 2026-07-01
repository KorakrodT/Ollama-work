@echo off
REM Build "LM Co-work.exe" (native window app, LM Studio backend)
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
chcp 65001 >nul

echo.
echo [1/5] Closing running app and cleaning old build/junk...
REM ปิดแอปที่เปิดค้าง ไม่งั้น .exe ถูกล็อก เขียนทับไม่ได้ (เหตุที่ dist ไม่อัปเดต)
taskkill /f /im "LM Co-work.exe" >nul 2>&1
timeout /t 1 /nobreak >nul 2>&1
REM ลบของเก่า/ไฟล์ขยะ (สร้างใหม่หมดทุกครั้ง = build สะอาด)
rmdir /s /q build >nul 2>&1
rmdir /s /q dist  >nul 2>&1
del /q res.txt *.bak *.bak-* >nul 2>&1

echo.
echo [2/5] Installing PyInstaller and libraries...
py -m pip install --upgrade pyinstaller ruff
py -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo [3/5] Lint (ruff --select F) - catches scope-shadowing bugs like the
echo       "import time" one that broke every launch of main() on 1 Jul 2026...
py -m ruff check --select F server.py tools.py agents.py agent_store.py data_store.py skills_loader.py mcp_client.py knowledge_store.py winproc.py
if errorlevel 1 goto error

echo.
echo [4/5] Compile-check (guard truncated/half-synced .py before building)...
py -m compileall -q server.py tools.py agents.py agent_store.py data_store.py skills_loader.py mcp_client.py knowledge_store.py winproc.py
if errorlevel 1 goto error

echo.
echo [5/5] Building "LM Co-work.exe" ...
py -m PyInstaller --onefile --noconfirm --clean --windowed --name "LM Co-work" --icon "icon.ico" --add-data "index.html;." --collect-all webview --collect-all pythonnet --hidden-import clr server.py
if errorlevel 1 goto error

if exist skills xcopy /e /i /y skills "dist\skills" >nul

echo.
echo ==========================================================
echo  DONE!  File:  %~dp0dist\LM Co-work.exe
echo  Note: no need to open LM Studio - the app auto-starts its
echo        headless server. Just install the CLI once
echo        ( npx lmstudio install-cli ) and have at least one
echo        model downloaded in LM Studio.
echo ==========================================================
echo.
pause
exit /b 0

:error
echo.
echo Build FAILED - please copy the messages above and send them.
echo.
pause