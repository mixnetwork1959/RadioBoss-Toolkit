# Changelog

## Version 0.2.3 – 2026-07-31

### Added

- Portable launcher for four independent RadioBOSS tools
- Broadcast Scheduler 4.5.1 with first-start SDL file selection
- RadioBOSS Library Cleaner 1.0.0
- Silence Scanner with a native Windows interface
- Auto Cutter with a native Windows interface and hidden processing engine
- Shared language selection: English, German, Dutch and Bulgarian
- Offline user guide in all four languages
- Help and About menus with versions, build, author and license
- Shared portable `toolkit_settings.json`
- Safety check before Auto Cutter can use a scanner report

### Improved

- Multiple tools can run simultaneously and independently
- FFmpeg and FFprobe run invisibly in the background
- Public Calendar editor and scheduler dialogs are translated
- Tool executables are located automatically if moved inside the toolkit folder

### Safety

- Silence Scanner never modifies original audio files
- Auto Cutter creates corrected copies and never overwrites originals
- Library Cleaner creates a backup before removing orphaned library entries
