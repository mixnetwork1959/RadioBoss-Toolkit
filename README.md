# RadioBOSS Toolkit

Version 0.3.0

A portable launcher for RadioBOSS broadcast, library and synchronization tools.

## Included tools

- Broadcast Scheduler
- RadioBOSS Library Cleaner
- Silence Scanner
- Auto Cutter
- RadioBOSS SongSync Engine 1.8.0

SongSync can now be started directly from the Toolkit. The SongSync card provides separate actions for **Sync now** and **Setup**, so the synchronization engine and its configuration wizard remain easy to access.

SongSync 1.8.0 uses `config.json` for its runtime configuration and includes the improved SFTP key setup workflow.

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

Do not place the toolkit in protected Windows folders such as `C:\Program Files` or `C:\Windows`. Windows may prevent the tools from saving settings, reports, and processed files.

Keep the complete folder structure together. You may create a desktop shortcut to `RadioBOSS Toolkit.exe`.

On its first start, Broadcast Scheduler asks you to select your RadioBOSS scheduler profile (`*.sdl`) and creates its own `settings.json`.

Silence Scanner has its own Windows interface with folder selection, progress, status information, and direct access to the finished CSV report.

Auto Cutter also runs in a Windows interface. Its FFmpeg processing engine is hidden in the background while progress and results remain visible in the app.

## Auto Cutter safety

Run Silence Scanner first and review `silence_report.csv`. Auto Cutter only starts from the launcher when a scanner report exists. It creates corrected copies and does not overwrite the original audio files.

## Requirements

- Windows 10 or Windows 11
- FFmpeg and FFprobe installed in `C:\ffmpeg` for the audio processing tools

## License

MIT License
