@echo off
setlocal
cd /d "%~dp0"

echo =====================================================
echo RadioBOSS Broadcast Scheduler 4.5.1 - Windows Build
echo =====================================================

py -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

if exist build_scheduler rmdir /s /q build_scheduler
if exist dist_scheduler rmdir /s /q dist_scheduler
if exist "RadioBOSS Broadcast Scheduler" rmdir /s /q "RadioBOSS Broadcast Scheduler"

py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --workpath "build_scheduler" ^
  --distpath "dist_scheduler" ^
  --name "RadioBOSS Broadcast Scheduler" ^
  --icon "assets\radioboss-toolkit.ico" ^
  --paths "." ^
  --paths "source" ^
  --add-data "source\BroadcastScheduler\templates;templates" ^
  "source\BroadcastScheduler\scheduler.py"
if errorlevel 1 goto :error

mkdir "RadioBOSS Broadcast Scheduler"
mkdir "RadioBOSS Broadcast Scheduler\help"
copy /y "dist_scheduler\RadioBOSS Broadcast Scheduler.exe" "RadioBOSS Broadcast Scheduler\"
copy /y "BROADCAST_SCHEDULER_README.md" "RadioBOSS Broadcast Scheduler\README.md"
copy /y "LICENSE" "RadioBOSS Broadcast Scheduler\"
copy /y "help\scheduler_*.html" "RadioBOSS Broadcast Scheduler\help\"

echo.
echo Build completed:
echo %CD%\RadioBOSS Broadcast Scheduler
echo.
echo This is the standalone freeware package.
if not defined CI pause
exit /b 0

:error
echo.
echo BUILD FAILED.
if not defined CI pause
exit /b 1
