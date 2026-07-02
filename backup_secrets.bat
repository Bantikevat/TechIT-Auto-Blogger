@echo off
REM ==============================================================
REM   TechIT Secrets Backup Script
REM   Ek click me saare 5 secret files ko ZIP karke Desktop pe save
REM ==============================================================
title TechIT Secrets Backup

echo.
echo ========================================
echo   TechIT Auto-Blogger — Backup
echo ========================================
echo.
echo Ye script 5 sensitive files ko zip karke Desktop par save karega.
echo Uske baad Gmail/Drive/USB me copy kar lena (safe rakhne ke liye).
echo.
pause

cd /d "%~dp0"

REM check files exist
for %%f in (blogger_credentials.json client_secrets.json gemini_api_key.txt imgbb_api_key.txt google_indexing_sa.json) do (
    if not exist "%%f" (
        echo.
        echo [ERROR] "%%f" file nahi mili!
        echo    Ye script sirf setup complete hone ke baad chalao.
        echo.
        pause
        exit /b 1
    )
)

REM get date for filename
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set DT=%%c-%%a-%%b
set OUTPUT=%USERPROFILE%\Desktop\techit-secrets-backup-%DT%.zip

REM delete old file if exists
if exist "%OUTPUT%" del "%OUTPUT%"

REM use PowerShell to zip
echo [INFO] Zip file banayi ja rahi hai...
powershell -NoProfile -Command "Compress-Archive -Path 'blogger_credentials.json','client_secrets.json','gemini_api_key.txt','imgbb_api_key.txt','google_indexing_sa.json' -DestinationPath '%OUTPUT%' -Force"

if exist "%OUTPUT%" (
    echo.
    echo ========================================
    echo   [SUCCESS] Backup ho gaya!
    echo ========================================
    echo.
    echo File location:
    echo   %OUTPUT%
    echo.
    echo Ab is file ko:
    echo   1. Gmail me khud ko email karo, YA
    echo   2. Google Drive private folder me upload karo, YA
    echo   3. USB drive me copy karo
    echo.
    echo Naye laptop pe SETUP_GUIDE.md follow karna.
    echo.
) else (
    echo.
    echo [ERROR] Zip banane me problem aayi.
    echo Manually 5 files ko folder me select karke "Send to > Compressed folder" karo.
    echo.
)

pause
