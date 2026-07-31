# ==========================================
# Broadcast Scheduler
# Version 4.5.1
# scheduler.py
# ==========================================

from pathlib import Path
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from config import load_settings, save_settings
from database import Database
from scheduler_controller import SchedulerController
from gui import show_events
from scheduler_i18n import language

VERSION = "4.5.1"

START_TEXT = {
"en":("RadioBOSS scheduler file required","Select the RadioBOSS scheduler profile you want to analyze.\n\nThe file can be named Admin.sdl or have the name of your RadioBOSS profile.","Select RadioBOSS scheduler profile","RadioBOSS scheduler profiles","All files"),
"de":("RadioBOSS-Schedulerdatei erforderlich","Wähle das RadioBOSS-Schedulerprofil aus, das analysiert werden soll.\n\nDie Datei kann Admin.sdl heißen oder den Namen deines RadioBOSS-Profils tragen.","RadioBOSS-Schedulerprofil auswählen","RadioBOSS-Schedulerprofile","Alle Dateien"),
"nl":("RadioBOSS-schedulerbestand vereist","Selecteer het RadioBOSS-schedulerprofiel dat je wilt analyseren.\n\nHet bestand kan Admin.sdl heten of de naam van je RadioBOSS-profiel hebben.","RadioBOSS-schedulerprofiel selecteren","RadioBOSS-schedulerprofielen","Alle bestanden"),
"bg":("Необходим е файл на RadioBOSS Scheduler","Изберете профила на RadioBOSS Scheduler за анализ.\n\nФайлът може да се казва Admin.sdl или да носи името на вашия RadioBOSS профил.","Избор на RadioBOSS Scheduler профил","RadioBOSS Scheduler профили","Всички файлове"),
"ro":("Este necesar fișierul RadioBOSS Scheduler","Selectați profilul RadioBOSS Scheduler pe care doriți să îl analizați.\n\nFișierul poate fi numit Admin.sdl sau poate avea numele profilului RadioBOSS.","Selectați profilul RadioBOSS Scheduler","Profiluri RadioBOSS Scheduler","Toate fișierele")}


def choose_scheduler_file(settings):
    """Ask for a RadioBOSS SDL profile when none is configured."""

    configured = str(settings.get("admin_sdl", "")).strip()
    if configured and Path(configured).is_file():
        return True

    root = tk.Tk()
    root.withdraw()
    root.update_idletasks()

    labels = START_TEXT.get(language(), START_TEXT["en"])
    messagebox.showinfo(
        labels[0], labels[1],
        parent=root,
    )

    initial_directory = Path.home()
    appdata = os.environ.get("APPDATA")
    if appdata:
        radioboss_directory = Path(appdata) / "djsoft.net"
        if radioboss_directory.is_dir():
            initial_directory = radioboss_directory

    selected = filedialog.askopenfilename(
        parent=root,
        title=labels[2],
        initialdir=str(initial_directory),
        filetypes=[
            (labels[3], "*.sdl"),
            (labels[4], "*.*"),
        ],
    )
    root.destroy()

    if not selected:
        return False

    settings["admin_sdl"] = selected
    save_settings(settings)
    return True


def main():

    print("=" * 45)
    print(f" Broadcast Scheduler v{VERSION}")
    print("=" * 45)

    # Load settings
    settings = load_settings()

    if not choose_scheduler_file(settings):
        print("No scheduler profile selected.")
        return

    # Open database
    db = Database(settings)

    # Load events
    events = db.load_events()
    print(f"Events loaded: {len(events)}")

    # Create controller
    controller = SchedulerController(events)

    # Generate current week
    runtimes = controller.refresh()
    print(f"RunTimes generated: {len(runtimes)}")

    print("Schedule analysis completed.")

    # Start GUI
    show_events(
        controller,
        runtimes,
        settings
    )


if __name__ == "__main__":
    main()
