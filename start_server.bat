@echo off
chcp 65001 >nul
title Prompt Factory - 启动服务

echo [2/2] 启动python 服务端
:: 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

:: 检查 Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

:: 启动后端服务器
echo [1/2] 启动 Flask 后端服务器 (端口 5000)...
cd /d "%~dp0server"
start "Flask Server" cmd /k "python run.py"