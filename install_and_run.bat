@echo off
chcp 65001 >nul
title Установка Монитора Ноутбука

echo ========================================================
echo   Программа установки Мониторинга и Управления Вентилятором
echo   Для Windows 11
echo ========================================================
echo.

:: Проверка прав администратора (опционально, но желательно для доступа к железу)
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Запущено от имени администратора.
) else (
    echo [ВНИМАНИЕ] Рекомендуется запускать от имени администратора для полного доступа к датчикам.
    echo Сейчас скрипт работает в обычном режиме.
)

echo.
echo [ШАГ 1] Проверка наличия Python...

python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Python найден.
    python --version
) else (
    echo [ОШИБКА] Python не найден в системе!
    echo Пожалуйста, установите Python с https://www.python.org/downloads/
    echo При установке обязательно поставьте галочку "Add Python to PATH".
    pause
    exit /b 1
)

echo.
echo [ШАГ 2] Установка необходимых библиотек (psutil)...
pip install psutil
if %errorLevel% neq 0 (
    echo [ОШИБКА] Не удалось установить библиотеки. Проверьте подключение к интернету.
    pause
    exit /b 1
)

echo.
echo [ШАГ 3] Создание ярлыка для автозапуска (опционально)...
:: Можно раскомментировать следующие строки, чтобы создать ярлык
:: echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\Shortcut.vbs"
:: echo sLinkFile = "%USERPROFILE%\Desktop\FanMonitor.lnk" >> "%TEMP%\Shortcut.vbs"
:: echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\Shortcut.vbs"
:: echo oLink.TargetPath = "%~dp0start_monitor.bat" >> "%TEMP%\Shortcut.vbs"
:: echo oLink.Save >> "%TEMP%\Shortcut.vbs"
:: cscript //nologo "%TEMP%\Shortcut.vbs"
:: del "%TEMP%\Shortcut.vbs"

echo.
echo ========================================================
echo   УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!
echo ========================================================
echo.
echo Теперь вы можете запустить программу командой:
echo    start_monitor.bat
echo.
echo Или просто запустить её сейчас? (Нажмите Y для запуска, любую другую клавишу для выхода)
set /p choice="Запустить сейчас? (Y/N): "
if /i "%choice%"=="Y" (
    goto :run_app
) else (
    exit /b 0
)

:run_app
echo.
echo Запуск сервера мониторинга...
python "%~dp0app.py"
pause
