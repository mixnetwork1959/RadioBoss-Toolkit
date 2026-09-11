# RadioBOSS Toolkit

Version 0.4.0

A free portable collection of RadioBOSS library, audio and synchronization tools for Windows.

## Included tools

- RadioBOSS Library Cleaner
- Silence Scanner
- Auto Cutter
- RadioBOSS SongSync Engine 1.7.2

The **Broadcast Scheduler is no longer bundled with the Toolkit**. It is distributed separately as its own freeware product so both downloads stay focused and easier to maintain.

## What changed in 0.4.0

- Toolkit window now opens centered on the monitor currently in use.
- Broadcast Scheduler was removed from the Toolkit launcher and package.
- The launcher now uses a cleaner 2 × 2 card layout.
- SongSync now has two equal-width actions: **Sync now** and **Setup**.
- Toolkit is explicitly distributed as freeware.

## SongSync

SongSync can be started directly from the Toolkit. Use **Sync now** to run a synchronization and **Setup** to open the configuration wizard.

SongSync 1.7.2 uses `config.py` for its runtime configuration and includes the improved SFTP key setup workflow. Windows OpenSSH uploads run in the background without opening a CMD window.

## Library Cleaner

Library Cleaner 1.0.1 remembers the last selected SQLite database path and reuses its folder when browsing again. Database passwords are never stored.

## Languages

- English
- Deutsch
- Nederlands
- Български
- Română

Select the shared interface language under `Settings > Language`.

## Installation

Extract the complete ZIP archive to a normal writable folder, for example:

- `C:\RadioBOSS Toolkit`
- `D:\RadioBOSS Toolkit`

Do not place the toolkit in protected Windows folders such as `C:\Program Files` or `C:\Windows`. Windows may prevent the tools from saving settings, reports and processed files.

Keep the complete folder structure together. You may create a desktop shortcut to `RadioBOSS Toolkit.exe`.

Silence Scanner has its own Windows interface with folder selection, progress, status information and direct access to the finished CSV report.

Auto Cutter also runs in a Windows interface. Its FFmpeg processing engine is hidden in the background while progress and results remain visible in the app.

## Auto Cutter safety

Run Silence Scanner first and review `silence_report.csv`. Auto Cutter only starts from the launcher when a scanner report exists. It creates corrected copies and does not overwrite the original audio files.

## Requirements

- Windows 10 or Windows 11
- FFmpeg and FFprobe installed in `C:\ffmpeg` for the audio processing tools

## Building the package

`build_toolkit.bat` creates the Windows Toolkit package without Broadcast Scheduler.

Before building, place the current SongSync executables in:

`packaging\SongSync\`

Required files:

- `RadioBOSS-SongSync.exe`
- `RadioBOSS-SongSync-Setup.exe`

The standalone Broadcast Scheduler can be built separately with `build_broadcast_scheduler.bat`.

## Price and license

**Freeware / Free Download**

MIT License. See `LICENSE`.
