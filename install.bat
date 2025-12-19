@echo off
chcp 65001 >nul
title Prompt Factory - 安装依赖

echo ========================================
echo   Prompt Factory 依赖安装脚本
echo ========================================
echo.

:: 安装后端依赖
echo [1/2] 安装 Python 后端依赖...
cd /d "%~dp0server"
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [错误] Python 依赖安装失败
    pause
    exit /b 1
)

echo.

:: 安装前端依赖
echo [2/2] 安装 Node.js 前端依赖...
cd /d "%~dp0client"
call npm install
if %errorlevel% neq 0 (
    echo [错误] Node.js 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo   依赖安装完成！
echo   运行 start.bat 启动服务
echo ========================================
pause
