@echo off
setlocal
cd /d "%~dp0"

echo =============================================
echo RadioBOSS Toolkit v0.4.0 - Windows Build
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

mkdir "RadioBOSS Toolkit\tools\Library Cleaner"
mkdir "RadioBOSS Toolkit\tools\Audio Toolkit"
mkdir "RadioBOSS Toolkit\tools\SongSync"

copy /y "dist\RadioBOSS Toolkit.exe" "RadioBOSS Toolkit\"
copy /y "dist\SilenceScanner.exe" "RadioBOSS Toolkit\tools\Audio Toolkit\"
copy /y "dist\AutoCutter.exe" "RadioBOSS Toolkit\tools\Audio Toolkit\"
copy /y "dist\AutoCutterEngine.exe" "RadioBOSS Toolkit\tools\Audio Toolkit\"
copy /y "dist\RadioBOSS-Library-Cleaner.exe" "RadioBOSS Toolkit\tools\Library Cleaner\"

rem SongSync is distributed with the Toolkit but built separately.
rem Place the two current SongSync executables in packaging\SongSync before building.
if not exist "packaging\SongSync\RadioBOSS-SongSync.exe" goto :songsync_missing
if not exist "packaging\SongSync\RadioBOSS-SongSync-Setup.exe" goto :songsync_missing
copy /y "packaging\SongSync\RadioBOSS-SongSync.exe" "RadioBOSS Toolkit\tools\SongSync\"
copy /y "packaging\SongSync\RadioBOSS-SongSync-Setup.exe" "RadioBOSS Toolkit\tools\SongSync\"

copy /y README.md "RadioBOSS Toolkit\"
copy /y LICENSE "RadioBOSS Toolkit\"
mkdir "RadioBOSS Toolkit\help"
copy /y "help\*.html" "RadioBOSS Toolkit\help\"

echo.
echo Build completed:
echo %CD%\RadioBOSS Toolkit
echo.
echo Broadcast Scheduler is not included in this package.
echo Build it separately with build_broadcast_scheduler.bat
pause
exit /b 0

:songsync_missing
echo.
echo SONGSYNC FILES MISSING.
echo Copy the current SongSync executables to:
echo %CD%\packaging\SongSync
echo.
echo Required files:
echo RadioBOSS-SongSync.exe
echo RadioBOSS-SongSync-Setup.exe
goto :error

:error
echo.
echo BUILD FAILED.
pause
exit /b 1
