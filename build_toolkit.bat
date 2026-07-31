@echo off
setlocal
cd /d "%~dp0"

echo =============================================
echo RadioBOSS Toolkit - Windows Build
echo =============================================

py -m pip install --upgrade pyinstaller pymysql
if errorlevel 1 goto :error

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "RadioBOSS Toolkit" rmdir /s /q "RadioBOSS Toolkit"

py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "RadioBOSS Toolkit" ^
  --icon "assets\radioboss-toolkit.ico" ^
  --add-data "assets\radioboss-toolkit.ico;assets" ^
  --add-data "help;help" launcher.py
if errorlevel 1 goto :error

py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "RadioBOSS-Library-Cleaner" ^
  --icon "assets\radioboss-toolkit.ico" ^
  --paths "source" ^
  --hidden-import pymysql ^
  "source\LibraryCleaner\main.py"
if errorlevel 1 goto :error

py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "BroadcastScheduler" ^
  --icon "assets\radioboss-toolkit.ico" ^
  --paths "source" ^
  --add-data "source\BroadcastScheduler\templates;templates" ^
  "source\BroadcastScheduler\scheduler.py"
if errorlevel 1 goto :error

py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "SilenceScanner" ^
  --icon "assets\radioboss-toolkit.ico" ^
  --add-data "assets\radioboss-toolkit.ico;assets" ^
  "source\silence_scanner_gui.py"
if errorlevel 1 goto :error

py -m PyInstaller --noconfirm --clean --onefile --console ^
  --name "AutoCutterEngine" ^
  --icon "assets\radioboss-toolkit.ico" "source\Auto_Cutter.py"
if errorlevel 1 goto :error

py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "AutoCutter" ^
  --icon "assets\radioboss-toolkit.ico" ^
  --add-data "assets\radioboss-toolkit.ico;assets" ^
  "source\autocutter_gui.py"
if errorlevel 1 goto :error

mkdir "RadioBOSS Toolkit\tools\Broadcast Scheduler"
mkdir "RadioBOSS Toolkit\tools\Library Cleaner"
mkdir "RadioBOSS Toolkit\tools\Audio Toolkit"

copy /y "dist\RadioBOSS Toolkit.exe" "RadioBOSS Toolkit\"
copy /y "dist\SilenceScanner.exe" "RadioBOSS Toolkit\tools\Audio Toolkit\"
copy /y "dist\AutoCutter.exe" "RadioBOSS Toolkit\tools\Audio Toolkit\"
copy /y "dist\AutoCutterEngine.exe" "RadioBOSS Toolkit\tools\Audio Toolkit\"
copy /y "dist\BroadcastScheduler.exe" "RadioBOSS Toolkit\tools\Broadcast Scheduler\"
copy /y "dist\RadioBOSS-Library-Cleaner.exe" "RadioBOSS Toolkit\tools\Library Cleaner\"
copy /y README.md "RadioBOSS Toolkit\"
copy /y LICENSE "RadioBOSS Toolkit\"
mkdir "RadioBOSS Toolkit\help"
copy /y "help\*.html" "RadioBOSS Toolkit\help\"

echo.
echo Build completed:
echo %CD%\RadioBOSS Toolkit
pause
exit /b 0

:error
echo.
echo BUILD FAILED.
pause
exit /b 1
