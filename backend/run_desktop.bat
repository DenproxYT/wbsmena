@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Запуск Смена WB...
python run_desktop.py

if errorlevel 1 (
    echo.
    echo Ошибка запуска. Проверьте run_desktop.log
    pause
)
