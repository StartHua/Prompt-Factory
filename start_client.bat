@echo off
chcp 65001 >nul
:: 启动前端开发服务器
echo [2/2] 启动 Vite 前端服务器 (端口 5173)...
cd /d "%~dp0client"
start "Vite Dev Server" cmd /k "npm run dev"

echo.
echo ========================================
echo   服务已启动！
echo   后端: http://localhost:5000
echo   前端: http://localhost:5173
echo ========================================
echo..

start http://localhost:5173
