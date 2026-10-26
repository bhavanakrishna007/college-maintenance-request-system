@echo off
title College Maintenance Web Portal - DBMS Mini Project
color 1F

echo =====================================================================
echo    COLLEGE MAINTENANCE WEB PORTAL (DBMS MINI PROJECT)
echo    Course Code: 24CS305 / CS3106 - DBMS Laboratory
echo =====================================================================
echo.

echo [1/3] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your system PATH. Please install Python 3.10+.
    pause
    exit /b
)

echo [2/3] Opening browser at http://127.0.0.1:5000 in 2 seconds...
start "" http://127.0.0.1:5000

echo [3/3] Starting Flask Web Server on http://127.0.0.1:5000 ...
cd /d "%~dp0"
python web/server.py

if %errorlevel% neq 0 (
    echo.
    echo [NOTE] Server terminated or encountered an error.
    pause
)
