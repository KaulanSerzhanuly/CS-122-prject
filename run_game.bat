@echo off
REM Snake of Despair - Windows Launcher
REM This batch file provides an easy way to run the game on Windows

echo Starting Snake of Despair...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11 or 3.12 from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Run the game
echo Launching Snake of Despair...
python -m snake_of_despair %*

REM If the game exits, pause to show any error messages
if %errorlevel% neq 0 (
    echo.
    echo Game exited with error code %errorlevel%
    pause
)
