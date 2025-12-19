@echo off
chcp 65001 >nul
:: Start frontend dev server
echo [2/2] Starting Vite frontend server (port 5173)...
cd /d "%~dp0client"
start "Vite Dev Server" cmd /k "npm run dev"

echo.
echo ========================================
echo   Services started!
echo   Backend: http://localhost:5000
echo   Frontend: http://localhost:5173
echo ========================================
echo.

start http://localhost:5173
