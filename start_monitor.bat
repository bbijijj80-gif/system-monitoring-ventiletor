@echo off
chcp 65001 >nul
title Мониторинг Ноутбука
echo Запуск мониторинга...
python "%~dp0app.py"
pause
