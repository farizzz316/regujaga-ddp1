@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo ==========================================================
echo REGUJAGA - TERBITKAN KE GITHUB PUBLIK
 echo Akun tujuan: farizzz316
 echo Nama repo  : regujaga-ddp1
 echo ==========================================================
echo.

where git >nul 2>nul
if errorlevel 1 (
    echo ERROR: Git belum terpasang.
    echo Instal dari https://git-scm.com/download/win
    goto :failed
)

where gh >nul 2>nul
if errorlevel 1 (
    echo ERROR: GitHub CLI belum terpasang.
    echo Instal dengan PowerShell: winget install --id GitHub.cli --exact
    echo Atau kunjungi https://cli.github.com/
    echo Setelah instal, tutup lalu buka terminal kembali.
    goto :failed
)

echo [1/6] Memeriksa autentikasi GitHub...
gh auth status >nul 2>nul
if errorlevel 1 (
    echo Login ke GitHub di browser yang muncul.
    gh auth login --hostname github.com --web
    if errorlevel 1 goto :failed
)

set "GH_LOGIN="
for /f "usebackq delims=" %%U in (`gh api user --jq .login`) do set "GH_LOGIN=%%U"
if /I not "%GH_LOGIN%"=="farizzz316" (
    echo ERROR: Login GitHub aktif adalah "%GH_LOGIN%", bukan "farizzz316".
    echo Jalankan: gh auth switch
    goto :failed
)

echo [2/6] Memeriksa identitas commit...
git config user.name >nul 2>nul
if errorlevel 1 (
    echo ERROR: Nama pembuat commit belum diatur.
    echo Jalankan: git config --global user.name "Nama Anda"
    goto :failed
)
git config user.email >nul 2>nul
if errorlevel 1 (
    echo ERROR: Email pembuat commit belum diatur.
    echo Jalankan: git config --global user.email "email-akun-github-anda"
    goto :failed
)

echo [3/6] Menyiapkan repositori lokal...
git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
    git init
    if errorlevel 1 goto :failed
)
git add .
if errorlevel 1 goto :failed
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "chore: initial ReguJaga MVP source code"
    if errorlevel 1 goto :failed
)
git rev-parse --verify HEAD >nul 2>nul
if errorlevel 1 (
    echo ERROR: Belum ada commit lokal. Pastikan folder proyek berisi file.
    goto :failed
)
git branch -M main
if errorlevel 1 goto :failed

echo [4/6] Memeriksa repositori di GitHub...
gh repo view farizzz316/regujaga-ddp1 >nul 2>nul
if errorlevel 1 (
    echo [5/6] Membuat repo PUBLIK dan mengunggah kode...
    gh repo create farizzz316/regujaga-ddp1 --public --description "ReguJaga - penjadwalan relawan berbasis Python, CSP dan backtracking untuk proyek DDP1 UI" --source "." --remote "origin" --push
    if errorlevel 1 goto :failed
) else (
    echo Repo sudah ada; memeriksa remote dan mengunggah...
    git remote get-url origin >nul 2>nul
    if errorlevel 1 (
        git remote add origin https://github.com/farizzz316/regujaga-ddp1.git
        if errorlevel 1 goto :failed
    )
    for /f "usebackq delims=" %%R in (`git remote get-url origin`) do set "ORIGIN_URL=%%R"
    echo(!ORIGIN_URL! | findstr /I /C:"farizzz316/regujaga-ddp1" >nul
    if errorlevel 1 (
        echo ERROR: Remote origin tidak menunjuk ke repo ReguJaga yang dimaksud.
        echo Periksa dengan: git remote -v
        goto :failed
    )
    git push -u origin main
    if errorlevel 1 goto :failed
)

echo [6/6] Memeriksa status publik...
gh repo view farizzz316/regujaga-ddp1 --json url,visibility --jq ".url + \" [\" + .visibility + \"]\""
if errorlevel 1 goto :failed

echo.
echo SELESAI. Repositori: https://github.com/farizzz316/regujaga-ddp1
echo Selanjutnya undang anggota via Settings ^> Collaborators.
pause
exit /b 0

:failed
echo.
echo Proses belum selesai. Perbaiki pesan ERROR di atas, lalu jalankan lagi.
pause
exit /b 1
