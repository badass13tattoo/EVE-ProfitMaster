@echo off
echo ==============================================
echo   EVE Profit Master - Development Startup
echo ==============================================

REM Проверяем существование .env файла
if not exist .env (
    echo ERROR: .env файл не найден!
    echo Скопируйте .env.example в .env и заполните настройки EVE SSO
    echo.
    pause
    exit /b 1
)

echo Запускаем Backend (Flask)...
cd /d "%~dp0"
call venv\Scripts\activate.bat
start /B python app.py

echo Ждем запуска backend...
timeout /t 3 /nobreak >nul

echo Запускаем Frontend (Vue.js)...
cd eve-production-tracker-frontend
start cmd /k "npm run serve"

echo.
echo ==============================================
echo   Серверы запущены:
echo   Backend:  http://localhost:5000  
echo   Frontend: http://localhost:8080
echo ==============================================
echo.
echo Нажмите любую клавишу для завершения...
pause >nul

REM Завершаем процессы (опционально)
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
