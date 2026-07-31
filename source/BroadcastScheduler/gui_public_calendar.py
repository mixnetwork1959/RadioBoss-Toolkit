# ==========================================
# Broadcast Scheduler
# Version 4.5.0
# gui_public_calendar.py
# ==========================================

import os
import subprocess
import sys
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import (
    ttk,
    messagebox,
    colorchooser,
    filedialog
)

from config import (
    get_default_export_directory,
    load_settings,
    save_settings
)

from public_calendar_config import (
    PublicCalendarConfig,
    PublicCalendarEntry
)
from public_calendar_engine import (
    PublicCalendarEngine
)
from website_generator import (
    PublicCalendarWebsiteGenerator
)
from scheduler_i18n import language

PC_TEXTS = {
"en":{"suggested":"Suggested Programs","selected":"Selected Programs","all":"All Events","search":"Search:","view":"View:","select_visible":"Select Visible","clear_visible":"Clear Visible","publish_web":"Publish Website","open_export":"Open Export Folder","choose_export":"Choose Export Folder","save":"Save","info":"Suggested Programs shows likely long music blocks. Select a program on the left and edit its public appearance on the right.","publish":"Publish","event":"RadioBOSS Event","editor":"Public Program Editor","public_name":"Public Name:","description":"Description:","color":"Color:","apply":"Apply","preview":"Live Preview","export_folder":"Export Folder","saved":"The export folder was saved.","folder":"Folder","open_failed":"The export folder could not be opened.","generate_failed":"The website could not be generated.","generated":"The public calendar website was generated.","file":"File","open_hint":"Use 'Open Export Folder' to open its location.","calendar":"Public Calendar","save_failed":"Could not save configuration:","config_saved":"Configuration saved.","selected_count":"Selected programs"},
"de":{"suggested":"Vorgeschlagene Programme","selected":"Ausgewählte Programme","all":"Alle Ereignisse","search":"Suche:","view":"Ansicht:","select_visible":"Sichtbare auswählen","clear_visible":"Sichtbare abwählen","publish_web":"Website veröffentlichen","open_export":"Exportordner öffnen","choose_export":"Exportordner wählen","save":"Speichern","info":"Vorgeschlagene Programme zeigt wahrscheinlich lange Musikblöcke. Links ein Programm auswählen und rechts die öffentliche Darstellung bearbeiten.","publish":"Veröffentlichen","event":"RadioBOSS-Ereignis","editor":"Öffentlicher Programmeditor","public_name":"Öffentlicher Name:","description":"Beschreibung:","color":"Farbe:","apply":"Übernehmen","preview":"Live-Vorschau","export_folder":"Exportordner","saved":"Der Exportordner wurde gespeichert.","folder":"Ordner","open_failed":"Der Exportordner konnte nicht geöffnet werden.","generate_failed":"Die Website konnte nicht erstellt werden.","generated":"Die öffentliche Kalender-Website wurde erstellt.","file":"Datei","open_hint":"Mit „Exportordner öffnen“ kannst du den Speicherort anzeigen.","calendar":"Öffentlicher Kalender","save_failed":"Konfiguration konnte nicht gespeichert werden:","config_saved":"Konfiguration gespeichert.","selected_count":"Ausgewählte Programme"},
"nl":{"suggested":"Voorgestelde programma's","selected":"Geselecteerde programma's","all":"Alle gebeurtenissen","search":"Zoeken:","view":"Beeld:","select_visible":"Zichtbare selecteren","clear_visible":"Zichtbare wissen","publish_web":"Website publiceren","open_export":"Exportmap openen","choose_export":"Exportmap kiezen","save":"Opslaan","info":"Voorgestelde programma's toont waarschijnlijke lange muziekblokken. Selecteer links een programma en bewerk rechts de openbare weergave.","publish":"Publiceren","event":"RadioBOSS-gebeurtenis","editor":"Openbare programma-editor","public_name":"Openbare naam:","description":"Beschrijving:","color":"Kleur:","apply":"Toepassen","preview":"Live voorbeeld","export_folder":"Exportmap","saved":"De exportmap is opgeslagen.","folder":"Map","open_failed":"De exportmap kon niet worden geopend.","generate_failed":"De website kon niet worden gemaakt.","generated":"De openbare kalenderwebsite is gemaakt.","file":"Bestand","open_hint":"Gebruik 'Exportmap openen' om de locatie te openen.","calendar":"Openbare kalender","save_failed":"Configuratie kon niet worden opgeslagen:","config_saved":"Configuratie opgeslagen.","selected_count":"Geselecteerde programma's"},
"bg":{"suggested":"Предложени програми","selected":"Избрани програми","all":"Всички събития","search":"Търсене:","view":"Изглед:","select_visible":"Избор на видимите","clear_visible":"Изчистване на видимите","publish_web":"Публикуване на сайта","open_export":"Отваряне на папката","choose_export":"Избор на папка","save":"Запазване","info":"Предложените програми показват вероятни дълги музикални блокове. Изберете програма вляво и редактирайте публичния ѝ вид вдясно.","publish":"Публикуване","event":"RadioBOSS събитие","editor":"Редактор на публичната програма","public_name":"Публично име:","description":"Описание:","color":"Цвят:","apply":"Прилагане","preview":"Преглед на живо","export_folder":"Папка за експортиране","saved":"Папката за експортиране е запазена.","folder":"Папка","open_failed":"Папката не може да бъде отворена.","generate_failed":"Уебсайтът не може да бъде създаден.","generated":"Уебсайтът на публичния календар е създаден.","file":"Файл","open_hint":"Използвайте „Отваряне на папката“, за да видите местоположението.","calendar":"Публичен календар","save_failed":"Конфигурацията не може да бъде запазена:","config_saved":"Конфигурацията е запазена.","selected_count":"Избрани програми"}}

def pt(key): return PC_TEXTS.get(language(), PC_TEXTS["en"])[key]


# =====================================================
# Public Calendar Tab
# =====================================================

class PublicCalendarTab:

    VIEW_SUGGESTED = pt("suggested")
    VIEW_SELECTED = pt("selected")
    VIEW_ALL = pt("all")

    def __init__(
        self,
        parent,
        events,
        runtimes,
        config_filename="public_calendar.json",
        settings=None
    ):

        self.parent = parent
        self.events = events
        self.runtimes = runtimes
        self.settings = (
            settings
            if settings is not None
            else load_settings()
        )

        self.config = PublicCalendarConfig(
            config_filename
        )
        self.config.load()

        self.engine = PublicCalendarEngine()

        self.rows = []
        self.current_row = None

        self.suggested_ids = self._detect_program_candidates()

        self.search_var = tk.StringVar()
        self.view_var = tk.StringVar(
            value=self.VIEW_SUGGESTED
        )

        self.editor_name_var = tk.StringVar()
        self.editor_description_var = tk.StringVar()
        self.editor_color_var = tk.StringVar(
            value="#4EA3FF"
        )
        self.editor_selected_var = tk.BooleanVar()

        self._build_gui()
        self._load_candidates()

    def apply_theme(self, theme):
        """
        Apply the application theme to native Tk widgets.

        The live website preview deliberately keeps its own dark
        website design, because it represents the generated page.
        """

        self.canvas.configure(
            bg=theme["background"]
        )

        self.description_text.configure(
            bg=theme["input"],
            fg=theme["text"],
            insertbackground=theme["text"],
            selectbackground=theme["selection"],
            selectforeground=theme["text"],
            highlightbackground=theme["border"],
            highlightcolor=theme["accent"]
        )

    # =================================================
    # Candidate Detection
    # =================================================

    def _detect_program_candidates(self):

        grouped = defaultdict(list)

        for runtime in self.runtimes:

            event = getattr(
                runtime,
                "event",
                None
            )

            if event is None:
                continue

            event_id = getattr(
                event,
                "id",
                ""
            )

            if not event_id:
                continue

            grouped[
                (
                    event_id,
                    runtime.start.date()
                )
            ].append(runtime)

        suggested = set()

        for (
            event_id,
            _date
        ), event_runtimes in grouped.items():

            event_runtimes.sort(
                key=lambda item: item.start
            )

            chain = []

            for runtime in event_runtimes:

                if runtime.start.minute != 0:
                    chain = []
                    continue

                if not chain:
                    chain = [runtime]
                    continue

                gap_minutes = (
                    runtime.start - chain[-1].start
                ).total_seconds() / 60

                if 50 <= gap_minutes <= 70:
                    chain.append(runtime)
                else:
                    chain = [runtime]

                if 2 <= len(chain) < 18:
                    suggested.add(event_id)

        suggested.update(
            self.config.selected_ids()
        )

        return suggested

    # =================================================
    # Build GUI
    # =================================================

    def _build_gui(self):

        self.frame = ttk.Frame(
            self.parent
        )

        self.frame.pack(
            fill="both",
            expand=True
        )

        # ---------------------------------------------
        # Toolbar
        # ---------------------------------------------

        toolbar = ttk.Frame(
            self.frame
        )

        toolbar.pack(
            fill="x",
            padx=8,
            pady=8
        )

        ttk.Label(
            toolbar,
            text=pt("search")
        ).pack(
            side="left",
            padx=(0, 5)
        )

        search_entry = ttk.Entry(
            toolbar,
            textvariable=self.search_var,
            width=26
        )

        search_entry.pack(
            side="left",
            padx=(0, 12)
        )

        ttk.Label(
            toolbar,
            text=pt("view")
        ).pack(
            side="left",
            padx=(0, 5)
        )

        view_combo = ttk.Combobox(
            toolbar,
            textvariable=self.view_var,
            values=(
                self.VIEW_SUGGESTED,
                self.VIEW_SELECTED,
                self.VIEW_ALL
            ),
            state="readonly",
            width=20
        )

        view_combo.pack(
            side="left",
            padx=(0, 12)
        )

        view_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._apply_filters()
        )

        ttk.Button(
            toolbar,
            text=pt("select_visible"),
            command=self.select_all
        ).pack(
            side="left",
            padx=2
        )

        ttk.Button(
            toolbar,
            text=pt("clear_visible"),
            command=self.clear_all
        ).pack(
            side="left",
            padx=2
        )

        ttk.Button(
            toolbar,
            text=pt("publish_web"),
            command=self.publish_website
        ).pack(
            side="right",
            padx=2
        )

        ttk.Button(
            toolbar,
            text=pt("open_export"),
            command=self.open_export_folder
        ).pack(
            side="right",
            padx=2
        )

        ttk.Button(
            toolbar,
            text=pt("choose_export"),
            command=self.choose_export_folder
        ).pack(
            side="right",
            padx=2
        )

        ttk.Button(
            toolbar,
            text=pt("save"),
            command=self.save
        ).pack(
            side="right",
            padx=2
        )

        self.search_var.trace_add(
            "write",
            lambda *args: self._apply_filters()
        )

        info = ttk.Label(
            self.frame,
            text=(
                pt("info")
            )
        )

        info.pack(
            fill="x",
            padx=8,
            pady=(0, 6)
        )

        # ---------------------------------------------
        # Main Split View
        # ---------------------------------------------

        main_pane = ttk.Panedwindow(
            self.frame,
            orient="horizontal"
        )

        main_pane.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 8)
        )

        self.left_panel = ttk.Frame(
            main_pane
        )

        self.right_panel = ttk.Frame(
            main_pane
        )

        main_pane.add(
            self.left_panel,
            weight=1
        )

        main_pane.add(
            self.right_panel,
            weight=2
        )

        self._build_event_list()
        self._build_editor()
        self._build_preview()

    # =================================================
    # Event List
    # =================================================

    def _build_event_list(self):

        header = ttk.Frame(
            self.left_panel
        )

        header.pack(
            fill="x",
            pady=(0, 4)
        )

        ttk.Label(
            header,
            text=pt("publish"),
            width=9
        ).pack(
            side="left"
        )

        ttk.Label(
            header,
            text=pt("event")
        ).pack(
            side="left"
        )

        body = ttk.Frame(
            self.left_panel
        )

        body.pack(
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            body,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            body,
            orient="vertical",
            command=self.canvas.yview
        )

        self.rows_frame = ttk.Frame(
            self.canvas
        )

        self.rows_window = self.canvas.create_window(
            (0, 0),
            window=self.rows_frame,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.rows_frame.bind(
            "<Configure>",
            self._update_scrollregion
        )

        self.canvas.bind(
            "<Configure>",
            self._resize_rows_frame
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self._on_mousewheel
        )

    # =================================================
    # Editor
    # =================================================

    def _build_editor(self):

        editor_box = ttk.LabelFrame(
            self.right_panel,
            text=pt("editor")
        )

        editor_box.pack(
            fill="x",
            padx=(8, 0),
            pady=(0, 8)
        )

        editor_box.columnconfigure(
            1,
            weight=1
        )

        ttk.Label(
            editor_box,
            text=pt("publish") + ":"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=8,
            pady=8
        )

        self.editor_publish_check = ttk.Checkbutton(
            editor_box,
            variable=self.editor_selected_var,
            command=self._editor_changed
        )

        self.editor_publish_check.grid(
            row=0,
            column=1,
            sticky="w",
            padx=8,
            pady=8
        )

        ttk.Label(
            editor_box,
            text=pt("public_name")
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=8,
            pady=6
        )

        self.editor_name_entry = ttk.Entry(
            editor_box,
            textvariable=self.editor_name_var
        )

        self.editor_name_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=8,
            pady=6
        )

        ttk.Label(
            editor_box,
            text=pt("description")
        ).grid(
            row=2,
            column=0,
            sticky="nw",
            padx=8,
            pady=6
        )

        self.description_text = tk.Text(
            editor_box,
            height=4,
            wrap="word"
        )

        self.description_text.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=8,
            pady=6
        )

        ttk.Label(
            editor_box,
            text=pt("color")
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=8,
            pady=8
        )

        color_frame = ttk.Frame(
            editor_box
        )

        color_frame.grid(
            row=3,
            column=1,
            sticky="w",
            padx=8,
            pady=8
        )

        self.editor_color_button = tk.Button(
            color_frame,
            text="#4EA3FF",
            width=12,
            relief="groove",
            command=self.choose_editor_color
        )

        self.editor_color_button.pack(
            side="left"
        )

        ttk.Button(
            color_frame,
            text=pt("apply"),
            command=self.apply_editor
        ).pack(
            side="left",
            padx=8
        )

        self.editor_name_var.trace_add(
            "write",
            lambda *args: self._editor_changed()
        )

        self._set_editor_state(False)

    # =================================================
    # Preview
    # =================================================

    def _build_preview(self):

        preview_box = ttk.LabelFrame(
            self.right_panel,
            text=pt("preview")
        )

        preview_box.pack(
            fill="both",
            expand=True,
            padx=(8, 0)
        )

        preview_body = ttk.Frame(
            preview_box
        )

        preview_body.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        self.preview_canvas = tk.Canvas(
            preview_body,
            bg="#111827",
            highlightthickness=0
        )

        preview_scroll = ttk.Scrollbar(
            preview_body,
            orient="vertical",
            command=self.preview_canvas.yview
        )

        self.preview_frame = tk.Frame(
            self.preview_canvas,
            bg="#111827"
        )

        self.preview_window = self.preview_canvas.create_window(
            (0, 0),
            window=self.preview_frame,
            anchor="nw"
        )

        self.preview_canvas.configure(
            yscrollcommand=preview_scroll.set
        )

        self.preview_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        preview_scroll.pack(
            side="right",
            fill="y"
        )

        self.preview_frame.bind(
            "<Configure>",
            lambda event: self.preview_canvas.configure(
                scrollregion=self.preview_canvas.bbox("all")
            )
        )

        self.preview_canvas.bind(
            "<Configure>",
            lambda event: self.preview_canvas.itemconfigure(
                self.preview_window,
                width=event.width
            )
        )

    # =================================================
    # Candidate Rows
    # =================================================

    def _load_candidates(self):

        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        self.rows = []

        candidates = self.config.build_event_candidates(
            self.events
        )

        for index, candidate in enumerate(candidates):

            row_frame = ttk.Frame(
                self.rows_frame
            )

            row_frame.grid(
                row=index,
                column=0,
                sticky="ew",
                pady=2
            )

            row_frame.columnconfigure(
                1,
                weight=1
            )

            selected_var = tk.BooleanVar(
                value=candidate["selected"]
            )

            check = ttk.Checkbutton(
                row_frame,
                variable=selected_var,
                command=lambda: self._row_selection_changed()
            )

            check.grid(
                row=0,
                column=0,
                sticky="w",
                padx=(0, 8)
            )

            event_text = candidate["internal_name"]

            if candidate["group_name"]:
                event_text += (
                    f"  [{candidate['group_name']}]"
                )

            event_button = ttk.Button(
                row_frame,
                text=event_text
            )

            event_button.grid(
                row=0,
                column=1,
                sticky="ew"
            )

            row = {
                "frame": row_frame,
                "event_id": candidate["event_id"],
                "internal_name": candidate["internal_name"],
                "group_name": candidate["group_name"],
                "selected_var": selected_var,
                "public_name": candidate["public_name"],
                "description": candidate["description"],
                "color": candidate["color"],
                "button": event_button
            }

            event_button.configure(
                command=lambda selected_row=row: self.select_row(
                    selected_row
                )
            )

            self.rows.append(row)

        self._apply_filters()
        self._refresh_preview()

        visible = self._visible_rows()

        if visible:
            self.select_row(
                visible[0]
            )

    # =================================================
    # Row Selection / Editor
    # =================================================

    def select_row(
        self,
        row
    ):

        self.apply_editor(
            refresh=False
        )

        self.current_row = row

        self.editor_selected_var.set(
            row["selected_var"].get()
        )

        self.editor_name_var.set(
            row["public_name"]
        )

        self.description_text.delete(
            "1.0",
            "end"
        )

        self.description_text.insert(
            "1.0",
            row["description"]
        )

        self.editor_color_var.set(
            row["color"]
        )

        self.editor_color_button.configure(
            text=row["color"]
        )

        self._apply_button_color(
            self.editor_color_button,
            row["color"]
        )

        self._set_editor_state(True)

    def apply_editor(
        self,
        refresh=True
    ):

        if self.current_row is None:
            return

        self.current_row["selected_var"].set(
            self.editor_selected_var.get()
        )

        public_name = self.editor_name_var.get().strip()

        if not public_name:
            public_name = self.current_row["internal_name"]

        self.current_row["public_name"] = public_name

        self.current_row["description"] = (
            self.description_text
            .get("1.0", "end")
            .strip()
        )

        self.current_row["color"] = (
            self.editor_color_var.get().strip()
            or "#4EA3FF"
        )

        if refresh:
            self._apply_filters()
            self._refresh_preview()

    def _editor_changed(self):

        if self.current_row is None:
            return

        self.root_after_preview()

    def root_after_preview(self):

        self.parent.after_cancel(
            getattr(
                self,
                "_preview_after_id",
                "after#0"
            )
        ) if hasattr(self, "_preview_after_id") else None

        self._preview_after_id = self.parent.after(
            250,
            lambda: self.apply_editor(
                refresh=True
            )
        )

    def _set_editor_state(
        self,
        enabled
    ):

        state = (
            "normal"
            if enabled
            else "disabled"
        )

        self.editor_publish_check.configure(
            state=state
        )

        self.editor_name_entry.configure(
            state=state
        )

        self.description_text.configure(
            state=state
        )

        self.editor_color_button.configure(
            state=state
        )

    # =================================================
    # Filters
    # =================================================

    def _apply_filters(self):

        search = self.search_var.get().strip().lower()
        view = self.view_var.get()

        visible_index = 0

        for row in self.rows:

            text = (
                f"{row['internal_name']} "
                f"{row['group_name']} "
                f"{row['public_name']}"
            ).lower()

            matches_search = (
                not search
                or search in text
            )

            if view == self.VIEW_SUGGESTED:

                matches_view = (
                    row["event_id"]
                    in self.suggested_ids
                )

            elif view == self.VIEW_SELECTED:

                matches_view = (
                    row["selected_var"].get()
                )

            else:

                matches_view = True

            if matches_search and matches_view:

                row["frame"].grid(
                    row=visible_index,
                    column=0,
                    sticky="ew",
                    pady=2
                )

                visible_index += 1

            else:

                row["frame"].grid_remove()

    # =================================================
    # Selection
    # =================================================

    def _row_selection_changed(self):

        self._apply_filters()
        self._refresh_preview()

    def select_all(self):

        for row in self._visible_rows():
            row["selected_var"].set(True)

        self._refresh_preview()

    def clear_all(self):

        for row in self._visible_rows():
            row["selected_var"].set(False)

        self._apply_filters()
        self._refresh_preview()

    def _visible_rows(self):

        return [
            row
            for row in self.rows
            if row["frame"].winfo_manager()
        ]

    # =================================================
    # Color
    # =================================================

    def choose_editor_color(self):

        selected = colorchooser.askcolor(
            color=self.editor_color_var.get(),
            title="Choose Public Calendar Color"
        )

        color = selected[1]

        if not color:
            return

        color = color.upper()

        self.editor_color_var.set(
            color
        )

        self.editor_color_button.configure(
            text=color
        )

        self._apply_button_color(
            self.editor_color_button,
            color
        )

        self.apply_editor()

    def _apply_button_color(
        self,
        button,
        color
    ):

        try:

            color = color.upper()

            red = int(color[1:3], 16)
            green = int(color[3:5], 16)
            blue = int(color[5:7], 16)

            brightness = (
                red * 299
                + green * 587
                + blue * 114
            ) / 1000

            foreground = (
                "black"
                if brightness >= 140
                else "white"
            )

            button.configure(
                bg=color,
                fg=foreground,
                activebackground=color,
                activeforeground=foreground
            )

        except (ValueError, IndexError):

            button.configure(
                bg="#4EA3FF",
                fg="white"
            )

    # =================================================
    # Preview Data
    # =================================================

    def _build_temporary_config(self):

        temp_config = PublicCalendarConfig(
            self.config.filename
        )

        for row in self.rows:

            if not row["selected_var"].get():
                continue

            temp_config.set_entry(
                PublicCalendarEntry(
                    event_id=row["event_id"],
                    public_name=(
                        row["public_name"]
                        or row["internal_name"]
                    ),
                    description=row["description"],
                    color=(
                        row["color"]
                        or "#4EA3FF"
                    ),
                    enabled=True
                )
            )

        return temp_config

    def _refresh_preview(self):

        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        temp_config = self._build_temporary_config()

        blocks = self.engine.detect(
            self.runtimes,
            temp_config
        )

        if not blocks:

            label = tk.Label(
                self.preview_frame,
                text=(
                    "Select one or more programs\n"
                    "to display the live preview."
                ),
                bg="#111827",
                fg="#D1D5DB",
                font=("Segoe UI", 12),
                justify="center"
            )

            label.pack(
                fill="x",
                padx=20,
                pady=30
            )

            return

        days = defaultdict(list)

        for block in blocks:
            days[
                block.start.strftime(
                    "%A"
                )
            ].append(block)

        day_order = (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        )

        for day in day_order:

            day_blocks = days.get(
                day,
                []
            )

            if not day_blocks:
                continue

            day_label = tk.Label(
                self.preview_frame,
                text=day,
                bg="#111827",
                fg="white",
                font=("Segoe UI", 15, "bold"),
                anchor="w"
            )

            day_label.pack(
                fill="x",
                padx=12,
                pady=(12, 6)
            )

            for block in day_blocks:

                self._create_preview_card(
                    block
                )

    def _create_preview_card(
        self,
        block
    ):

        color = (
            block.color
            or "#4EA3FF"
        )

        card = tk.Frame(
            self.preview_frame,
            bg=color,
            bd=1,
            relief="solid"
        )

        card.pack(
            fill="x",
            padx=12,
            pady=4
        )

        text_color = self._contrast_color(
            color
        )

        time_label = tk.Label(
            card,
            text=(
                f"{block.start:%H:%M} – "
                f"{block.end:%H:%M}"
            ),
            bg=color,
            fg=text_color,
            font=("Segoe UI", 9),
            anchor="w"
        )

        time_label.pack(
            fill="x",
            padx=10,
            pady=(8, 2)
        )

        name_label = tk.Label(
            card,
            text=block.public_name,
            bg=color,
            fg=text_color,
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        )

        name_label.pack(
            fill="x",
            padx=10,
            pady=(0, 2)
        )

        if block.description:

            description_label = tk.Label(
                card,
                text=block.description,
                bg=color,
                fg=text_color,
                font=("Segoe UI", 9),
                anchor="w",
                justify="left",
                wraplength=500
            )

            description_label.pack(
                fill="x",
                padx=10,
                pady=(0, 8)
            )

        else:

            spacer = tk.Frame(
                card,
                bg=color,
                height=6
            )

            spacer.pack(
                fill="x"
            )

    def _contrast_color(
        self,
        color
    ):

        try:

            red = int(color[1:3], 16)
            green = int(color[3:5], 16)
            blue = int(color[5:7], 16)

            brightness = (
                red * 299
                + green * 587
                + blue * 114
            ) / 1000

            return (
                "#000000"
                if brightness >= 140
                else "#FFFFFF"
            )

        except (ValueError, IndexError):

            return "#FFFFFF"

    # =================================================
    # Publish Website
    # =================================================

    def _export_directory(self):

        configured = self.settings.get(
            "export_directory",
            ""
        )

        if configured:
            return Path(configured).expanduser()

        return get_default_export_directory()

    def choose_export_folder(self):

        current_directory = self._export_directory()

        selected = filedialog.askdirectory(
            parent=self.parent.winfo_toplevel(),
            title=pt("choose_export"),
            initialdir=str(current_directory)
        )

        if not selected:
            return

        self.settings["export_directory"] = selected
        save_settings(self.settings)

        messagebox.showinfo(
            pt("export_folder"),
            (
                f"{pt('saved')}\n\n{pt('folder')}:\n{selected}"
            )
        )

    def open_export_folder(self):

        export_directory = self._export_directory()

        try:
            export_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            if os.name == "nt":
                os.startfile(str(export_directory))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(export_directory)])
            else:
                subprocess.Popen(["xdg-open", str(export_directory)])

        except (OSError, subprocess.SubprocessError) as error:
            messagebox.showerror(
                pt("open_export"),
                (
                    f"{pt('open_failed')}\n\n"
                    f"{pt('folder')}:\n{export_directory}\n\n"
                    f"{error}"
                )
            )

    def publish_website(self):

        self.apply_editor(
            refresh=False
        )

        if not self._save_configuration(
            show_message=False
        ):
            return

        try:

            generator = PublicCalendarWebsiteGenerator(
                station_name="Radio Albena",
                station_tagline=(
                    "The Sound of the Black Sea Coast"
                ),
                timezone_name="Europe/Sofia"
            )

            output_file = generator.generate(
                open_browser=True,
                output_directory=self._export_directory()
            )

        except Exception as error:

            messagebox.showerror(
                pt("publish_web"),
                (
                    f"{pt('generate_failed')}\n\n"
                    f"{error}"
                )
            )

            return

        messagebox.showinfo(
            pt("publish_web"),
            (
                f"{pt('generated')}\n\n"
                f"{pt('file')}:\n{output_file}\n\n"
                f"{pt('open_hint')}"
            )
        )

    def _save_configuration(
        self,
        show_message=True
    ):

        self.config.entries = {}
        selected_count = 0

        for row in self.rows:

            if not row["selected_var"].get():
                continue

            self.config.set_entry(
                PublicCalendarEntry(
                    event_id=row["event_id"],
                    public_name=(
                        row["public_name"]
                        or row["internal_name"]
                    ),
                    description=row["description"],
                    color=(
                        row["color"]
                        or "#4EA3FF"
                    ),
                    enabled=True
                )
            )

            selected_count += 1

        try:
            self.config.save()
        except OSError as error:
            messagebox.showerror(
                pt("calendar"),
                f"{pt('save_failed')}\n\n{error}"
            )
            return False

        if show_message:
            messagebox.showinfo(
                pt("calendar"),
                (
                    f"{pt('config_saved')}\n\n"
                    f"{pt('selected_count')}: {selected_count}\n"
                    f"{pt('file')}: {self.config.filename}"
                )
            )

        return True

    # =================================================
    # Save
    # =================================================

    def save(self):

        self.apply_editor(
            refresh=False
        )

        self._save_configuration(
            show_message=True
        )

    # =================================================
    # Canvas Helpers
    # =================================================

    def _update_scrollregion(
        self,
        event=None
    ):

        self.canvas.configure(
            scrollregion=self.canvas.bbox(
                "all"
            )
        )

    def _resize_rows_frame(
        self,
        event
    ):

        self.canvas.itemconfigure(
            self.rows_window,
            width=event.width
        )

    def _on_mousewheel(
        self,
        event
    ):

        if not self.canvas.winfo_ismapped():
            return

        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )
