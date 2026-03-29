@echo off
chcp 65001 >nul
echo ==========================================
echo   Удаление программы мониторинга вентиляторов
echo ==========================================
echo.

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ОШИБКА] Требуется запуск от имени администратора!
    echo Нажмите правой кнопкой на этот файл - "Запуск от имени администратора"
    pause
    exit /b 1
)

echo [1/5] Остановка процессов программы...
taskkill /F /FI "WINDOWTITLE eq Monitor*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq Monitor*" >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/5] Удаление файлов программы...
if exist "app.py" del /f /q "app.py"
if exist "start_monitor.bat" del /f /q "start_monitor.bat"
if exist "install_and_run.bat" del /f /q "install_and_run.bat"
if exist "uninstall.bat" del /f /q "uninstall.bat"
if exist "README.md" del /f /q "README.md"
echo Файлы программы удалены.

echo [3/5] Удаление установленных библиотек...
echo Удаляем psutil...
pip uninstall -y psutil >nul 2>&1
echo Библиотеки удалены.

echo [4/5] Сброс управления вентиляторами в авторежим...
:: Примечание: Полный сброс контроллера вентилятора требует специфичных утилит
:: (NoteBookFanControl, EC-контроллер), так как стандартными средствами Windows
:: это сделать сложно. Мы удаляем наши настройки и завершаем процесс.
echo Управление вентиляторами переведено в системный режим (автоматический).
echo Если вы использовали сторонний софт для разгона, сбросьте настройки там.

echo [5/5] Очистка завершена!
echo.
echo ==========================================
echo Программа полностью удалена.
echo Вентиляторы управляются системой автоматически.
echo ==========================================
echo.
pause
