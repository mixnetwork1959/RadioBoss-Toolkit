from __future__ import annotations

import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .database import MySQLDatabase, SQLiteDatabase
from .cleaner import clean_orphaned_entries
from .i18n import text
from .scanner import scan_libraries
from toolkit_common import LANGUAGES, load_toolkit_settings, save_language, toolkit_root


class CleanerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.language = tk.StringVar(value=load_toolkit_settings()["language"])
        self.database_type = tk.StringVar(value="sqlite")
        self.sqlite_path = tk.StringVar()
        self.host = tk.StringVar(value="127.0.0.1")
        self.port = tk.StringVar(value="3306")
        self.database_name = tk.StringVar(value="radioboss")
        self.user = tk.StringVar(value="root")
        self.password = tk.StringVar()
        self.status = tk.StringVar()
        self.last_result = None
        self._build()
        self._translate()
        self._build_menu()

    def _build(self) -> None:
        self.root.geometry("900x600")
        self.root.minsize(760, 480)
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        top = ttk.Frame(main)
        top.pack(fill="x")
        ttk.Radiobutton(top, text="SQLite", variable=self.database_type,
                        value="sqlite", command=self._switch_database).pack(side="left")
        ttk.Radiobutton(top, text="MySQL", variable=self.database_type,
                        value="mysql", command=self._switch_database).pack(side="left", padx=8)

        self.connection = ttk.LabelFrame(main, padding=10)
        self.connection.pack(fill="x", pady=10)
        self.sqlite_frame = ttk.Frame(self.connection)
        self.sqlite_frame.pack(fill="x")
        self.sqlite_label = ttk.Label(self.sqlite_frame)
        self.sqlite_label.pack(side="left")
        ttk.Entry(self.sqlite_frame, textvariable=self.sqlite_path).pack(side="left", fill="x", expand=True, padx=8)
        self.browse_button = ttk.Button(self.sqlite_frame, command=self._browse)
        self.browse_button.pack(side="right")

        self.mysql_frame = ttk.Frame(self.connection)
        fields = (("Host", self.host, 18, False), ("Port", self.port, 7, False),
                  ("Database", self.database_name, 15, False), ("User", self.user, 12, False),
                  ("Password", self.password, 15, True))
        for label, variable, width, secret in fields:
            ttk.Label(self.mysql_frame, text=label).pack(side="left", padx=(0, 3))
            ttk.Entry(self.mysql_frame, textvariable=variable, width=width,
                      show="*" if secret else "").pack(side="left", padx=(0, 9))

        buttons = ttk.Frame(main)
        buttons.pack(fill="x")
        self.clean_button = ttk.Button(buttons, command=self._clean, state="disabled")
        self.clean_button.pack(side="right")
        self.scan_button = ttk.Button(buttons, command=self._scan)
        self.scan_button.pack(side="right", padx=(0, 8))

        columns = ("library", "entries", "orphans")
        self.tree = ttk.Treeview(main, columns=columns, show="tree headings")
        self.tree.heading("#0", text="ID")
        self.tree.column("#0", width=70, stretch=False)
        self.tree.column("library", width=360)
        self.tree.column("entries", width=100, anchor="e")
        self.tree.column("orphans", width=100, anchor="e")
        self.tree.pack(fill="both", expand=True, pady=10)
        ttk.Label(main, textvariable=self.status, anchor="w").pack(fill="x")
        self._switch_database()

    def _build_menu(self) -> None:
        lang = self.language.get()
        menu = tk.Menu(self.root)
        settings_menu = tk.Menu(menu, tearoff=False)
        language_menu = tk.Menu(settings_menu, tearoff=False)
        for code, label in LANGUAGES.items():
            language_menu.add_radiobutton(
                label=label, value=code, variable=self.language,
                command=lambda value=code: self._set_language(value),
            )
        settings_menu.add_cascade(label=text(lang, "language"), menu=language_menu)
        menu.add_cascade(label=text(lang, "settings"), menu=settings_menu)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label=text(lang, "user_guide"), command=self._open_guide)
        help_menu.add_command(label=text(lang, "open_folder"), command=self._open_folder)
        help_menu.add_separator()
        help_menu.add_command(label=text(lang, "about"), command=self._about)
        menu.add_cascade(label=text(lang, "help"), menu=help_menu)
        self.root.configure(menu=menu)

    def _set_language(self, language: str) -> None:
        self.language.set(language)
        save_language(language)
        self._translate()
        self._build_menu()

    def _open_guide(self) -> None:
        guide = toolkit_root() / "help" / f"index_{self.language.get()}.html"
        if guide.is_file() and os.name == "nt":
            os.startfile(guide)  # type: ignore[attr-defined]
        else:
            messagebox.showwarning(text(self.language.get(), "help"), str(guide))

    def _open_folder(self) -> None:
        if os.name == "nt":
            os.startfile(toolkit_root())  # type: ignore[attr-defined]

    def _about(self) -> None:
        messagebox.showinfo(
            text(self.language.get(), "about"),
            "RadioBOSS Library Cleaner\nVersion 1.0.0\nBuild: 2026-07-31\n\n"
            "Created by Raymond Ummels\nDeveloped with assistance from OpenAI ChatGPT\n\n"
            "© 2026 Raymond Ummels\nMIT License",
        )

    def _translate(self) -> None:
        lang = self.language.get()
        self.root.title(text(lang, "title"))
        self.connection.configure(text=text(lang, "database"))
        self.sqlite_label.configure(text=text(lang, "sqlite_file"))
        self.browse_button.configure(text=text(lang, "browse"))
        self.scan_button.configure(text=text(lang, "scan"))
        self.clean_button.configure(text=text(lang, "clean"))
        self.tree.heading("library", text=text(lang, "library"))
        self.tree.heading("entries", text=text(lang, "entries"))
        self.tree.heading("orphans", text=text(lang, "orphans"))
        self.status.set(text(lang, "ready"))

    def _switch_database(self) -> None:
        if self.database_type.get() == "sqlite":
            self.mysql_frame.pack_forget()
            self.sqlite_frame.pack(fill="x")
        else:
            self.sqlite_frame.pack_forget()
            self.mysql_frame.pack(fill="x")

    def _browse(self) -> None:
        path = filedialog.askopenfilename(filetypes=(("SQLite database", "*.db"), ("All files", "*.*")))
        if path:
            self.sqlite_path.set(path)

    def _database(self, read_only: bool = True):
        if self.database_type.get() == "sqlite":
            return SQLiteDatabase(self.sqlite_path.get(), read_only=read_only)
        return MySQLDatabase(self.host.get(), int(self.port.get()), self.database_name.get(),
                             self.user.get(), self.password.get())

    def _scan(self) -> None:
        lang = self.language.get()
        self.scan_button.configure(state="disabled")
        self.status.set(text(lang, "scanning"))
        self.root.update_idletasks()
        try:
            with self._database() as database:
                result = scan_libraries(database)
            self.last_result = result
            self.tree.delete(*self.tree.get_children())
            for library in result.libraries:
                parent = self.tree.insert("", "end", text=str(library.library_id), values=(
                    library.library_name, library.total_entries, len(library.orphaned)))
                for orphan in library.orphaned:
                    self.tree.insert(parent, "end", text=str(orphan.track_id),
                                     values=(orphan.filename, "", ""))
            self.status.set(text(lang, "finished", libraries=result.library_count,
                                 tracks=result.tracks_count, orphans=result.orphan_count))
            self.clean_button.configure(state="normal" if result.orphan_count else "disabled")
        except Exception as exc:
            messagebox.showerror(text(lang, "error"), str(exc))
            self.status.set(str(exc))
        finally:
            self.scan_button.configure(state="normal")

    def _clean(self) -> None:
        lang = self.language.get()
        if self.last_result is None or self.last_result.orphan_count == 0:
            messagebox.showinfo(text(lang, "confirm_title"), text(lang, "nothing"))
            return
        if not messagebox.askyesno(
            text(lang, "confirm_title"),
            text(lang, "confirm", orphans=self.last_result.orphan_count),
        ):
            return
        self.scan_button.configure(state="disabled")
        self.clean_button.configure(state="disabled")
        try:
            with self._database(read_only=False) as database:
                _, deleted, backups = clean_orphaned_entries(database)
            backup = str(backups[-1].parent) if backups else "-"
            messagebox.showinfo(
                text(lang, "confirm_title"),
                text(lang, "cleaned", deleted=deleted, backup=backup),
            )
            self._scan()
        except Exception as exc:
            messagebox.showerror(text(lang, "error"), str(exc))
            self.status.set(str(exc))
        finally:
            self.scan_button.configure(state="normal")


def run() -> None:
    root = tk.Tk()
    CleanerApp(root)
    root.mainloop()
