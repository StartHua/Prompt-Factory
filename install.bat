@echo off
chcp 65001 >nul
title Prompt Factory - Install

echo ========================================
echo   Prompt Factory - Installing...
echo ========================================
echo.

:: Install backend dependencies
echo [1/2] Installing Python dependencies...
cd /d "%~dp0server"
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [Error] Python dependencies install failed
    pause
    exit /b 1
)

echo.

:: Install frontend dependencies
echo [2/2] Installing Node.js dependencies...
cd /d "%~dp0client"
call npm install
if %errorlevel% neq 0 (
    echo [Error] Node.js dependencies install failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation complete!
echo   Run start_server.bat and start_client.bat
echo ========================================
pause
