@echo off
title College Maintenance and Request System - DBMS Mini Project
color 1F

:MENU
cls
echo =====================================================================
echo    COLLEGE MAINTENANCE AND REQUEST SYSTEM (DBMS MINI PROJECT)
echo    Course Code: 24CS305 / CS3106 - DBMS Laboratory
echo =====================================================================
echo.
echo Please choose which application interface you would like to run:
echo.
echo   [1] Modern Web Portal (Recommended - HTML5, CSS3, Chart.js)
echo   [2] Desktop GUI Application (Python Tkinter)
echo   [3] Initialize / Reset MySQL Database & Sample Data
echo   [4] Run Full System & Web API Test Suite
echo   [5] Exit
echo.
echo =====================================================================
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto RUN_WEB
if "%choice%"=="2" goto RUN_DESKTOP
if "%choice%"=="3" goto RUN_SETUP
if "%choice%"=="4" goto RUN_TESTS
if "%choice%"=="5" exit /b
goto MENU

:RUN_WEB
cls
echo Starting Modern Web Portal at http://127.0.0.1:5000 ...
start "" http://127.0.0.1:5000
python web/server.py
pause
goto MENU

:RUN_DESKTOP
cls
echo Starting Tkinter Desktop Application...
python src/app.py
pause
goto MENU

:RUN_SETUP
cls
echo Initializing MySQL Database (college_maintenance_db)...
python database/setup_database.py
pause
goto MENU

:RUN_TESTS
cls
echo Running Backend Integration & Web API Test Suites...
python tests/test_system.py
echo.
python tests/test_web_api.py
pause
goto MENU
