@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py run.py
) else (
    python run.py
)
set "rc=%errorlevel%"
if not "%rc%"=="0" (
    echo.
    echo ReguJaga gagal dibuka. Pastikan Python 3.10+ dan tkinter tersedia.
    pause
)
exit /b %rc%
