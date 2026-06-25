@echo off
title TechIT Auto-Blogger Publisher
echo [INFO] Activating Python virtual environment...
cd /d "c:\Claude\AI_"
call .venv\Scripts\activate

echo [INFO] Running Auto-Posting Script...
python auto_post_blogger.py

echo.
echo ==================================================
echo [INFO] Script Execution Completed.
echo ==================================================
pause
