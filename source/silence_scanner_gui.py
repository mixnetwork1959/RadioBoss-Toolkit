"""Windows interface for the Silence Scanner engine."""

from __future__ import annotations

import os
import queue
import sys
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import silence_scanner as engine
from toolkit_common import LANGUAGES, load_toolkit_settings, save_language, toolkit_root


GUI_VERSION = "1.0.0"

TEXTS = {
    "en": {"title":"Silence Scanner", "subtitle":"Find long intros and problematic outros without changing original files.", "music":"Music folder", "browse":"Browse…", "start":"Start Scan", "report":"Open Report", "select":"Select a music folder to begin.", "preparing":"Preparing scan…", "settings":"Settings", "language":"Language", "help":"Help", "guide":"User Guide", "folder":"Open Toolkit Folder", "about":"About Silence Scanner", "invalid":"Select a valid music folder first.", "required":"Music folder required", "ffmpeg":"FFmpeg not found", "running":"A scan is currently running.", "no_files":"No supported audio files were found.", "failed":"Scan could not be completed.", "completed":"Scan completed", "scanned":"Files scanned", "problems":"Problem files", "intro":"Long intro", "outro":"Bad outro", "both":"Both", "errors":"Errors", "report_path":"Report", "complete_msg":"The scan is complete.", "not_found":"Report not found"},
    "de": {"title":"Silence Scanner", "subtitle":"Lange Intros und problematische Outros finden, ohne Originaldateien zu verändern.", "music":"Musikordner", "browse":"Durchsuchen…", "start":"Scan starten", "report":"Bericht öffnen", "select":"Wähle zuerst einen Musikordner aus.", "preparing":"Scan wird vorbereitet…", "settings":"Einstellungen", "language":"Sprache", "help":"Hilfe", "guide":"Benutzerhandbuch", "folder":"Toolkit-Ordner öffnen", "about":"Über Silence Scanner", "invalid":"Bitte zuerst einen gültigen Musikordner auswählen.", "required":"Musikordner erforderlich", "ffmpeg":"FFmpeg nicht gefunden", "running":"Ein Scan läuft gerade.", "no_files":"Keine unterstützten Audiodateien gefunden.", "failed":"Der Scan konnte nicht abgeschlossen werden.", "completed":"Scan abgeschlossen", "scanned":"Dateien gescannt", "problems":"Problemdateien", "intro":"Langes Intro", "outro":"Schlechtes Outro", "both":"Beides", "errors":"Fehler", "report_path":"Bericht", "complete_msg":"Der Scan ist abgeschlossen.", "not_found":"Bericht nicht gefunden"},
    "nl": {"title":"Silence Scanner", "subtitle":"Vind lange intro's en problematische outro's zonder originele bestanden te wijzigen.", "music":"Muziekmap", "browse":"Bladeren…", "start":"Scan starten", "report":"Rapport openen", "select":"Selecteer eerst een muziekmap.", "preparing":"Scan voorbereiden…", "settings":"Instellingen", "language":"Taal", "help":"Help", "guide":"Gebruikershandleiding", "folder":"Toolkit-map openen", "about":"Over Silence Scanner", "invalid":"Selecteer eerst een geldige muziekmap.", "required":"Muziekmap vereist", "ffmpeg":"FFmpeg niet gevonden", "running":"Er wordt momenteel gescand.", "no_files":"Geen ondersteunde audiobestanden gevonden.", "failed":"De scan kon niet worden voltooid.", "completed":"Scan voltooid", "scanned":"Bestanden gescand", "problems":"Probleembestanden", "intro":"Lange intro", "outro":"Slechte outro", "both":"Beide", "errors":"Fouten", "report_path":"Rapport", "complete_msg":"De scan is voltooid.", "not_found":"Rapport niet gevonden"},
    "bg": {"title":"Silence Scanner", "subtitle":"Откриване на дълги интрота и проблемни аутрота без промяна на оригиналите.", "music":"Папка с музика", "browse":"Избор…", "start":"Старт на сканирането", "report":"Отваряне на отчета", "select":"Първо изберете папка с музика.", "preparing":"Подготовка на сканирането…", "settings":"Настройки", "language":"Език", "help":"Помощ", "guide":"Ръководство", "folder":"Отваряне на папката", "about":"За Silence Scanner", "invalid":"Първо изберете валидна папка с музика.", "required":"Необходима е папка", "ffmpeg":"FFmpeg не е намерен", "running":"В момента се извършва сканиране.", "no_files":"Не са намерени поддържани аудиофайлове.", "failed":"Сканирането не можа да завърши.", "completed":"Сканирането завърши", "scanned":"Сканирани файлове", "problems":"Проблемни файлове", "intro":"Дълго интро", "outro":"Лошо аутро", "both":"И двете", "errors":"Грешки", "report_path":"Отчет", "complete_msg":"Сканирането приключи.", "not_found":"Отчетът не е намерен"},
    "ro": {"title":"Silence Scanner", "subtitle":"Detectează intro-uri lungi și outro-uri problematice fără a modifica fișierele originale.", "music":"Folder muzică", "browse":"Răsfoire…", "start":"Pornește scanarea", "report":"Deschide raportul", "select":"Selectați mai întâi un folder cu muzică.", "preparing":"Se pregătește scanarea…", "settings":"Setări", "language":"Limbă", "help":"Ajutor", "guide":"Ghid de utilizare", "folder":"Deschide folderul Toolkit", "about":"Despre Silence Scanner", "invalid":"Selectați mai întâi un folder valid cu muzică.", "required":"Este necesar un folder cu muzică", "ffmpeg":"FFmpeg nu a fost găsit", "running":"O scanare este în curs.", "no_files":"Nu au fost găsite fișiere audio acceptate.", "failed":"Scanarea nu a putut fi finalizată.", "completed":"Scanare finalizată", "scanned":"Fișiere scanate", "problems":"Fișiere problematice", "intro":"Intro lung", "outro":"Outro problematic", "both":"Ambele", "errors":"Erori", "report_path":"Raport", "complete_msg":"Scanarea s-a încheiat.", "not_found":"Raportul nu a fost găsit"},
}


def resource_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


class ScannerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.language = load_toolkit_settings()["language"]
        self.language_var = tk.StringVar(value=self.language)
        self.running = False
        self.title(f"{self._t('title')} v{GUI_VERSION}")
        self.geometry("760x560")
        self.minsize(680, 500)
        self.configure(bg="#eef2f7")
        self.events: queue.Queue = queue.Queue()
        self.folder_var = tk.StringVar()
        self.status_var = tk.StringVar(value=self._t("select"))
        self.progress_var = tk.DoubleVar(value=0)
        self._set_icon()
        self._styles()
        self._menu()
        self._ui()
        self.after(100, self._process_events)

    def _t(self, key: str) -> str:
        return TEXTS.get(self.language, TEXTS["en"])[key]

    def _menu(self) -> None:
        menu = tk.Menu(self)
        settings = tk.Menu(menu, tearoff=False)
        languages = tk.Menu(settings, tearoff=False)
        for code, label in LANGUAGES.items():
            languages.add_radiobutton(label=label, value=code, variable=self.language_var,
                                      command=lambda value=code: self._set_language(value))
        settings.add_cascade(label=self._t("language"), menu=languages)
        menu.add_cascade(label=self._t("settings"), menu=settings)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label=self._t("guide"), command=self._open_guide)
        help_menu.add_command(label=self._t("folder"), command=lambda: os.startfile(toolkit_root()))
        help_menu.add_separator()
        help_menu.add_command(label=self._t("about"), command=self._about)
        menu.add_cascade(label=self._t("help"), menu=help_menu)
        self.configure(menu=menu)

    def _set_language(self, language: str) -> None:
        if self.running:
            self.language_var.set(self.language)
            messagebox.showinfo(self._t("title"), self._t("running"))
            return
        self.language = language
        self.language_var.set(language)
        save_language(language)
        self.title(f"{self._t('title')} v{GUI_VERSION}")
        for child in self.winfo_children():
            child.destroy()
        self.status_var.set(self._t("select"))
        self._menu()
        self._ui()

    def _open_guide(self) -> None:
        guide = toolkit_root() / "help" / f"index_{self.language}.html"
        if guide.is_file(): os.startfile(guide)
        else: messagebox.showwarning(self._t("help"), str(guide))

    def _about(self) -> None:
        messagebox.showinfo(self._t("about"), f"Silence Scanner GUI\nVersion {GUI_VERSION}\nBuild: 2026-07-31\n\nCreated by Raymond Ummels\nDeveloped with assistance from OpenAI ChatGPT\n\n© 2026 Raymond Ummels\nMIT License")

    def _set_icon(self) -> None:
        try:
            self.iconbitmap(default=str(resource_dir() / "assets" / "radioboss-toolkit.ico"))
        except tk.TclError:
            pass

    def _styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#eef2f7")
        style.configure("Title.TLabel", background="#eef2f7", foreground="#07153d",
                        font=("Segoe UI", 22, "bold"))
        style.configure("Text.TLabel", background="#eef2f7", foreground="#526176",
                        font=("Segoe UI", 10))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=(15, 8))
        style.map("Action.TButton", background=[("active", "#ffb563"), ("!disabled", "#ff9f43")],
                  foreground=[("!disabled", "#07153d")])
        style.configure("Scan.Horizontal.TProgressbar", troughcolor="#dbe3ed",
                        background="#ff9f43", lightcolor="#ff9f43", darkcolor="#ff9f43")

    def _ui(self) -> None:
        main = ttk.Frame(self, style="App.TFrame", padding=28)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text=self._t("title"), style="Title.TLabel").pack(anchor="w")
        ttk.Label(main, text=self._t("subtitle"),
                  style="Text.TLabel").pack(anchor="w", pady=(2, 22))

        ttk.Label(main, text=self._t("music"), style="Text.TLabel").pack(anchor="w")
        path_row = ttk.Frame(main, style="App.TFrame")
        path_row.pack(fill="x", pady=(5, 15))
        self.path_entry = ttk.Entry(path_row, textvariable=self.folder_var)
        self.path_entry.pack(side="left", fill="x", expand=True)
        self.browse_button = ttk.Button(path_row, text=self._t("browse"), command=self._browse)
        self.browse_button.pack(side="left", padx=(8, 0))

        button_row = ttk.Frame(main, style="App.TFrame")
        button_row.pack(fill="x")
        self.start_button = ttk.Button(button_row, text=self._t("start"), style="Action.TButton",
                                       command=self._start)
        self.start_button.pack(side="left")
        self.report_button = ttk.Button(button_row, text=self._t("report"), command=self._open_report,
                                        state="disabled")
        self.report_button.pack(side="left", padx=(10, 0))

        self.progress = ttk.Progressbar(main, variable=self.progress_var, maximum=100,
                                        style="Scan.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(22, 7))
        ttk.Label(main, textvariable=self.status_var, style="Text.TLabel").pack(anchor="w")

        log_frame = ttk.Frame(main, padding=1)
        log_frame.pack(fill="both", expand=True, pady=(14, 0))
        self.log = tk.Text(log_frame, height=12, wrap="word", state="disabled",
                           font=("Consolas", 9), bg="white", fg="#1b2a41",
                           relief="flat", padx=12, pady=10)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _browse(self) -> None:
        selected = filedialog.askdirectory(title="Select music folder", mustexist=True)
        if selected:
            self.folder_var.set(selected)

    def _start(self) -> None:
        folder = self.folder_var.get().strip().strip('"')
        if not Path(folder).is_dir():
            messagebox.showwarning(self._t("required"), self._t("invalid"))
            return
        if not Path(engine.FFMPEG).is_file():
            messagebox.showerror(self._t("ffmpeg"), f"{self._t('ffmpeg')}:\n\n{engine.FFMPEG}")
            return

        self._set_running(True)
        self.progress_var.set(0)
        self.status_var.set(self._t("preparing"))
        self._clear_log()
        self._append_log(f"Music folder: {folder}\n")
        threading.Thread(target=self._scan_worker, args=(folder,), daemon=True).start()

    def _scan_worker(self, folder: str) -> None:
        try:
            files = list(engine.audio_files(folder))
            if not files:
                self.events.put(("error", self._t("no_files")))
                return
            self.events.put(("log", f"Found {len(files):,} audio files.\nScan started…\n\n"))
            engine.reset_stats()
            started = time.time()
            rows = engine.scan_library(files, self._progress_from_worker)
            engine.save_csv(rows)
            elapsed = time.time() - started
            self.events.put(("done", rows, elapsed))
        except Exception as error:
            self.events.put(("error", str(error)))

    def _progress_from_worker(self, current: int, total: int, eta: float, filename: str) -> None:
        self.events.put(("progress", current, total, eta, filename))

    def _process_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "progress":
                    _, current, total, eta, filename = event
                    self.progress_var.set(current / total * 100)
                    self.status_var.set(
                        f"{current:,} of {total:,} files  •  {current / total * 100:.1f}%  •  "
                        f"ETA {engine.format_time(eta)}"
                    )
                    if current == 1 or current % 100 == 0 or current == total:
                        self._append_log(f"[{current:,}/{total:,}] {Path(filename).name}\n")
                elif kind == "log":
                    self._append_log(event[1])
                elif kind == "done":
                    self._finish(event[1], event[2])
                elif kind == "error":
                    self._set_running(False)
                    self.status_var.set(self._t("failed"))
                    messagebox.showerror(self._t("title"), event[1])
        except queue.Empty:
            pass
        self.after(100, self._process_events)

    def _finish(self, rows, elapsed: float) -> None:
        self._set_running(False)
        self.progress_var.set(100)
        self.status_var.set(f"{self._t('completed')}: {engine.format_time(elapsed)}")
        report = Path.cwd() / engine.CSV_FILE
        self.report_button.configure(state="normal")
        summary = (
            f"\n{self._t('completed')}\n"
            f"{self._t('scanned')}: {engine.stats['files']:,}\n"
            f"{self._t('problems')}: {len(rows):,}\n"
            f"{self._t('intro')}: {engine.stats['long_intro']:,}\n"
            f"{self._t('outro')}: {engine.stats['bad_outro']:,}\n"
            f"{self._t('both')}: {engine.stats['both']:,}\n"
            f"{self._t('errors')}: {engine.stats['errors']:,}\n"
            f"{self._t('report_path')}: {report}\n"
        )
        self._append_log(summary)
        messagebox.showinfo(self._t("completed"), f"{self._t('complete_msg')}\n\n{self._t('problems')}: {len(rows):,}")

    def _set_running(self, running: bool) -> None:
        self.running = running
        state = "disabled" if running else "normal"
        self.start_button.configure(state=state)
        self.browse_button.configure(state=state)
        self.path_entry.configure(state=state)

    def _open_report(self) -> None:
        report = Path.cwd() / engine.CSV_FILE
        if report.is_file() and os.name == "nt":
            os.startfile(report)  # type: ignore[attr-defined]
        elif not report.is_file():
            messagebox.showwarning(self._t("not_found"), str(report))

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")


if __name__ == "__main__":
    ScannerApp().mainloop()
