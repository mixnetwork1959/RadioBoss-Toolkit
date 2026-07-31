"""Windows interface for Auto Cutter."""

from __future__ import annotations

import csv
import os
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from toolkit_common import LANGUAGES, load_toolkit_settings, save_language, toolkit_root


VERSION = "1.0.0"
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
CSV_FILE = APP_DIR / "silence_report.csv"
CUT_REPORT = APP_DIR / "cut_report.csv"
ENGINE = APP_DIR / "AutoCutterEngine.exe"

TEXTS = {
 "en":{"title":"Auto Cutter","subtitle":"Create corrected copies from a reviewed Silence Scanner report.","settings":"Settings","language":"Language","help":"Help","guide":"User Guide","folder_menu":"Open Toolkit Folder","about":"About Auto Cutter","loading":"Loading Silence Scanner report…","start":"Start Auto Cutter","open_output":"Open Output Folder","open_report":"Open Cut Report","missing":"Scanner report: not found","run_scanner":"Run Silence Scanner first.","entries":"Scanner report: {count:,} entries  •  {date}","output":"Output folder: {path}","review":"Review the scanner report before starting Auto Cutter.","read_error":"Scanner report could not be read","engine_missing":"Processing engine not found","confirm_title":"Start Auto Cutter?","confirm":"Auto Cutter will process {count:,} report entries and create copies.\n\nOriginal audio files will not be overwritten.\n\nContinue?","running":"Auto Cutter is running…","processing":"Processing {current:,} of {total:,} files…","start_error":"Auto Cutter could not be started.","success":"Auto Cutter finished successfully.","complete":"Processing is complete. Original files were not changed.","failed":"Auto Cutter finished with an error. See the log for details.","failed_msg":"Processing did not complete successfully.","language_locked":"Processing is currently running."},
 "de":{"title":"Auto Cutter","subtitle":"Korrigierte Kopien aus einem geprüften Silence-Scanner-Bericht erstellen.","settings":"Einstellungen","language":"Sprache","help":"Hilfe","guide":"Benutzerhandbuch","folder_menu":"Toolkit-Ordner öffnen","about":"Über Auto Cutter","loading":"Silence-Scanner-Bericht wird geladen…","start":"Auto Cutter starten","open_output":"Ausgabeordner öffnen","open_report":"Schnittbericht öffnen","missing":"Scanner-Bericht: nicht gefunden","run_scanner":"Bitte zuerst den Silence Scanner ausführen.","entries":"Scanner-Bericht: {count:,} Einträge  •  {date}","output":"Ausgabeordner: {path}","review":"Prüfe den Scanner-Bericht, bevor du den Auto Cutter startest.","read_error":"Scanner-Bericht konnte nicht gelesen werden","engine_missing":"Verarbeitungsmodul nicht gefunden","confirm_title":"Auto Cutter starten?","confirm":"Auto Cutter verarbeitet {count:,} Berichtseinträge und erstellt Kopien.\n\nOriginaldateien werden nicht überschrieben.\n\nFortfahren?","running":"Auto Cutter läuft…","processing":"Datei {current:,} von {total:,} wird verarbeitet…","start_error":"Auto Cutter konnte nicht gestartet werden.","success":"Auto Cutter wurde erfolgreich abgeschlossen.","complete":"Die Verarbeitung ist abgeschlossen. Originaldateien wurden nicht verändert.","failed":"Auto Cutter wurde mit einem Fehler beendet. Einzelheiten stehen im Protokoll.","failed_msg":"Die Verarbeitung wurde nicht erfolgreich abgeschlossen.","language_locked":"Die Verarbeitung läuft gerade."},
 "nl":{"title":"Auto Cutter","subtitle":"Maak gecorrigeerde kopieën vanuit een gecontroleerd Silence Scanner-rapport.","settings":"Instellingen","language":"Taal","help":"Help","guide":"Gebruikershandleiding","folder_menu":"Toolkit-map openen","about":"Over Auto Cutter","loading":"Silence Scanner-rapport laden…","start":"Auto Cutter starten","open_output":"Uitvoermap openen","open_report":"Kniprapport openen","missing":"Scannerrapport: niet gevonden","run_scanner":"Voer eerst Silence Scanner uit.","entries":"Scannerrapport: {count:,} items  •  {date}","output":"Uitvoermap: {path}","review":"Controleer het scannerrapport voordat Auto Cutter wordt gestart.","read_error":"Scannerrapport kon niet worden gelezen","engine_missing":"Verwerkingsmodule niet gevonden","confirm_title":"Auto Cutter starten?","confirm":"Auto Cutter verwerkt {count:,} rapportitems en maakt kopieën.\n\nOriginele audiobestanden worden niet overschreven.\n\nDoorgaan?","running":"Auto Cutter is actief…","processing":"Bestand {current:,} van {total:,} verwerken…","start_error":"Auto Cutter kon niet worden gestart.","success":"Auto Cutter is succesvol voltooid.","complete":"De verwerking is voltooid. Originele bestanden zijn niet gewijzigd.","failed":"Auto Cutter is met een fout afgesloten. Zie het logboek.","failed_msg":"De verwerking is niet succesvol voltooid.","language_locked":"De verwerking is momenteel actief."},
 "bg":{"title":"Auto Cutter","subtitle":"Създаване на коригирани копия от проверен отчет на Silence Scanner.","settings":"Настройки","language":"Език","help":"Помощ","guide":"Ръководство","folder_menu":"Отваряне на папката","about":"За Auto Cutter","loading":"Зареждане на отчета…","start":"Старт на Auto Cutter","open_output":"Отваряне на изходната папка","open_report":"Отваряне на отчета","missing":"Отчетът не е намерен","run_scanner":"Първо стартирайте Silence Scanner.","entries":"Отчет: {count:,} записа  •  {date}","output":"Изходна папка: {path}","review":"Проверете отчета преди стартиране на Auto Cutter.","read_error":"Отчетът не може да бъде прочетен","engine_missing":"Модулът за обработка не е намерен","confirm_title":"Стартиране на Auto Cutter?","confirm":"Auto Cutter ще обработи {count:,} записа и ще създаде копия.\n\nОригиналните файлове няма да бъдат презаписани.\n\nПродължаване?","running":"Auto Cutter работи…","processing":"Обработка на файл {current:,} от {total:,}…","start_error":"Auto Cutter не можа да стартира.","success":"Auto Cutter завърши успешно.","complete":"Обработката приключи. Оригиналните файлове не са променени.","failed":"Auto Cutter завърши с грешка. Вижте дневника.","failed_msg":"Обработката не завърши успешно.","language_locked":"В момента се извършва обработка."}
}


def resource_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


class CutterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.language = load_toolkit_settings()["language"]
        self.language_var = tk.StringVar(value=self.language)
        self.running = False
        self.title(f"{self._t('title')} v{VERSION}")
        self.geometry("760x560")
        self.minsize(680, 500)
        self.configure(bg="#eef2f7")
        self.events: queue.Queue = queue.Queue()
        self.output_dir: Path | None = None
        self.total_rows = 0
        self.status_var = tk.StringVar(value=self._t("loading"))
        self.report_var = tk.StringVar()
        self.output_var = tk.StringVar(value="Output folder: —")
        self.progress_var = tk.DoubleVar(value=0)
        self._set_icon()
        self._styles()
        self._menu()
        self._ui()
        self._load_report()
        self.after(100, self._process_events)

    def _t(self, key: str, **values) -> str:
        return TEXTS.get(self.language, TEXTS["en"])[key].format(**values)

    def _menu(self) -> None:
        menu=tk.Menu(self); settings=tk.Menu(menu,tearoff=False); languages=tk.Menu(settings,tearoff=False)
        for code,label in LANGUAGES.items():
            languages.add_radiobutton(label=label,value=code,variable=self.language_var,command=lambda value=code:self._set_language(value))
        settings.add_cascade(label=self._t("language"),menu=languages); menu.add_cascade(label=self._t("settings"),menu=settings)
        help_menu=tk.Menu(menu,tearoff=False); help_menu.add_command(label=self._t("guide"),command=self._open_guide); help_menu.add_command(label=self._t("folder_menu"),command=lambda:os.startfile(toolkit_root())); help_menu.add_separator(); help_menu.add_command(label=self._t("about"),command=self._about); menu.add_cascade(label=self._t("help"),menu=help_menu); self.configure(menu=menu)

    def _set_language(self, language: str) -> None:
        if self.running:
            self.language_var.set(self.language); messagebox.showinfo(self._t("title"),self._t("language_locked")); return
        self.language=language; self.language_var.set(language); save_language(language); self.title(f"{self._t('title')} v{VERSION}")
        for child in self.winfo_children(): child.destroy()
        self._menu(); self._ui(); self._load_report()

    def _open_guide(self) -> None:
        guide=toolkit_root()/"help"/f"index_{self.language}.html"
        if guide.is_file(): os.startfile(guide)
        else: messagebox.showwarning(self._t("help"),str(guide))

    def _about(self) -> None:
        messagebox.showinfo(self._t("about"),f"Auto Cutter GUI\nVersion {VERSION}\nBuild: 2026-07-31\n\nCreated by Raymond Ummels\nDeveloped with assistance from OpenAI ChatGPT\n\n© 2026 Raymond Ummels\nMIT License")

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
        style.configure("Cut.Horizontal.TProgressbar", troughcolor="#dbe3ed",
                        background="#ff9f43", lightcolor="#ff9f43", darkcolor="#ff9f43")

    def _ui(self) -> None:
        main = ttk.Frame(self, style="App.TFrame", padding=28)
        main.pack(fill="both", expand=True)
        ttk.Label(main, text=self._t("title"), style="Title.TLabel").pack(anchor="w")
        ttk.Label(main, text=self._t("subtitle"),
                  style="Text.TLabel").pack(anchor="w", pady=(2, 18))
        ttk.Label(main, textvariable=self.report_var, style="Text.TLabel").pack(anchor="w", pady=2)
        ttk.Label(main, textvariable=self.output_var, style="Text.TLabel").pack(anchor="w", pady=2)

        row = ttk.Frame(main, style="App.TFrame")
        row.pack(fill="x", pady=(16, 0))
        self.start_button = ttk.Button(row, text=self._t("start"), style="Action.TButton",
                                       command=self._start, state="disabled")
        self.start_button.pack(side="left")
        self.folder_button = ttk.Button(row, text=self._t("open_output"), command=self._open_folder,
                                        state="disabled")
        self.folder_button.pack(side="left", padx=(10, 0))
        self.report_button = ttk.Button(row, text=self._t("open_report"), command=self._open_cut_report,
                                        state="disabled")
        self.report_button.pack(side="left", padx=(10, 0))

        ttk.Progressbar(main, variable=self.progress_var, maximum=100,
                        style="Cut.Horizontal.TProgressbar").pack(fill="x", pady=(22, 7))
        ttk.Label(main, textvariable=self.status_var, style="Text.TLabel").pack(anchor="w")

        frame = ttk.Frame(main, padding=1)
        frame.pack(fill="both", expand=True, pady=(14, 0))
        self.log = tk.Text(frame, height=13, wrap="word", state="disabled",
                           font=("Consolas", 9), bg="white", fg="#1b2a41",
                           relief="flat", padx=12, pady=10)
        scroll = ttk.Scrollbar(frame, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _load_report(self) -> None:
        if not CSV_FILE.is_file():
            self.report_var.set(self._t("missing")); self.status_var.set(self._t("run_scanner"))
            return
        try:
            with CSV_FILE.open(newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle, delimiter=";"))
            self.total_rows = len(rows)
            modified = datetime.fromtimestamp(CSV_FILE.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            self.report_var.set(self._t("entries",count=self.total_rows,date=modified))
            if rows and rows[0].get("File"):
                root = Path(rows[0]["File"]).parent.parent
                self.output_dir = root / "Music_Cut"
                self.output_var.set(self._t("output",path=self.output_dir))
            self.status_var.set(self._t("review"))
            self.start_button.configure(state="normal" if rows else "disabled")
        except (OSError, csv.Error) as error:
            self.report_var.set(self._t("read_error"))
            self.status_var.set(str(error))

    def _start(self) -> None:
        if not ENGINE.is_file():
            messagebox.showerror(self._t("title"), f"{self._t('engine_missing')}:\n\n{ENGINE}")
            return
        if not messagebox.askyesno(
            self._t("confirm_title"), self._t("confirm",count=self.total_rows),
            icon="warning",
        ):
            return
        self.start_button.configure(state="disabled")
        self.progress_var.set(0)
        self.running=True; self.status_var.set(self._t("running"))
        self._clear_log()
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            process = subprocess.Popen(
                [str(ENGINE)], cwd=str(APP_DIR), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                creationflags=flags,
            )
            assert process.stdout is not None
            for line in process.stdout:
                self.events.put(("line", line))
            self.events.put(("done", process.wait()))
        except OSError as error:
            self.events.put(("error", str(error)))

    def _process_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "line":
                    line = event[1]
                    self._append_log(line)
                    if line.startswith("[") and "/" in line:
                        try:
                            position = line.split("]", 1)[0].strip("[")
                            current, total = (int(value) for value in position.split("/"))
                            self.progress_var.set(current / total * 100)
                            self.status_var.set(self._t("processing",current=current,total=total))
                        except (ValueError, ZeroDivisionError):
                            pass
                elif event[0] == "done":
                    self._finished(event[1])
                elif event[0] == "error":
                    self.start_button.configure(state="normal")
                    self.running=False; self.status_var.set(self._t("start_error")); messagebox.showerror(self._t("title"), event[1])
        except queue.Empty:
            pass
        self.after(100, self._process_events)

    def _finished(self, return_code: int) -> None:
        self.running=False
        self.start_button.configure(state="normal")
        if return_code == 0:
            self.progress_var.set(100)
            self.status_var.set(self._t("success"))
            if self.output_dir and self.output_dir.is_dir():
                self.folder_button.configure(state="normal")
            if CUT_REPORT.is_file():
                self.report_button.configure(state="normal")
            messagebox.showinfo(self._t("title"), self._t("complete"))
        else:
            self.status_var.set(self._t("failed")); messagebox.showerror(self._t("title"), self._t("failed_msg"))

    def _open_folder(self) -> None:
        if self.output_dir and self.output_dir.is_dir() and os.name == "nt":
            os.startfile(self.output_dir)  # type: ignore[attr-defined]

    def _open_cut_report(self) -> None:
        if CUT_REPORT.is_file() and os.name == "nt":
            os.startfile(CUT_REPORT)  # type: ignore[attr-defined]

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
    CutterApp().mainloop()
