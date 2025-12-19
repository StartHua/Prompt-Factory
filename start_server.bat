@echo off
chcp 65001 >nul
title Prompt Factory - Server

echo [1/2] Starting Python backend server...

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python not found, please install Python 3.11+
    pause
    exit /b 1
)

:: Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Node.js not found, please install Node.js
    pause
    exit /b 1
)

:: Start backend server
echo Starting Flask backend server (port 5000)...
cd /d "%~dp0server"
start "Flask Server" cmd /k "python run.py"
