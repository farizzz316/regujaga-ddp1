@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py run.py
) else (
    python run.py
)
if errorlevel 1 (
    echo.
    echo ReguJaga gagal dibuka. Pastikan Python 3.10+ dan tkinter tersedia.
    pause
)
