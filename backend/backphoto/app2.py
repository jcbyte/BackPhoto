# ! Untested modernised tkk app

import os
import shutil
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable

from .adb import ADB
from .config_manager import ConfigManager
from .file_tools import move
from .photo_tools import set_photos_exif_time
from .scanner import scan_device

# Constants
TOP_PADDING = 10
GROUPED_PADDING = 5
SEPARATED_PADDING = 15
GLOBAL_PADX = 10
FONT_LABEL = ("Segoe UI", 11)
FONT_ENTRY = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 10)


class BackPhotoApp(tk.Tk):
    """Main application class for GUI"""

    def __init__(self) -> None:
        super().__init__()

        # Load config
        self.config = ConfigManager("./config.json")

        # Connect to ADB server
        self.adb = ADB()

        # Set window properties
        self.title("BackPhoto")
        self.geometry("850x600")
        self.minsize(700, 500)
        icon = tk.PhotoImage(file="icon.png")
        self.iconphoto(True, icon)

        # Use notebook tabs instead of switching frames
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Add pages
        self.start_page = StartPage(self.notebook, self)
        self.options_page = OptionsPage(self.notebook, self)
        self.notebook.add(self.start_page, text="Start")
        self.notebook.add(self.options_page, text="Options")

    def update_gui_thread_safe(self, callback: Callable) -> None:
        """Run GUI function from a separate thread, safely."""
        self.after(0, callback)


class StartPage(ttk.Frame):
    """Main page where the user selects options and begins backup."""

    def __init__(self, parent: ttk.Widget, controller: BackPhotoApp):
        super().__init__(parent)
        self.controller = controller

        # ===== Device Selection Frame =====
        device_frame = ttk.LabelFrame(self, text="ADB Device", padding=(GLOBAL_PADX, TOP_PADDING))
        device_frame.grid(row=0, column=0, sticky="ew", padx=GLOBAL_PADX, pady=(TOP_PADDING, SEPARATED_PADDING))
        device_frame.grid_columnconfigure(0, weight=1)

        self.adb_device_dropdown = ttk.Combobox(device_frame, width=30, state="readonly", font=FONT_ENTRY)
        self.adb_device_dropdown.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.adb_device_refresh_button = ttk.Button(device_frame, text="Refresh", width=12, command=self.refresh_adb_devices)
        self.adb_device_refresh_button.grid(row=0, column=1, sticky="w")

        # ===== Destination Frame =====
        dest_frame = ttk.LabelFrame(self, text="Destination Path", padding=(GLOBAL_PADX, TOP_PADDING))
        dest_frame.grid(row=1, column=0, sticky="ew", padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))
        dest_frame.grid_columnconfigure(0, weight=1)

        self.destination_entry = ttk.Entry(dest_frame, font=FONT_ENTRY)
        self.destination_entry.grid(row=0, column=0, sticky="ew")

        # ===== Actions Frame =====
        action_frame = ttk.Frame(self)
        action_frame.grid(row=2, column=0, sticky="ew", padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))
        action_frame.grid_columnconfigure(0, weight=1)

        self.options_button = ttk.Button(action_frame, text="Options", width=15, command=lambda: controller.notebook.select(controller.options_page))
        self.options_button.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.start_button = ttk.Button(action_frame, text="Start Backup", width=25, command=lambda: threading.Thread(target=self.back_photos).start())
        self.start_button.grid(row=0, column=1, sticky="e")

        # ===== Progress Bar =====
        self.progress_bar_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, mode="determinate", variable=self.progress_bar_var)
        self.progress_bar.grid(row=3, column=0, sticky="ew", padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))

        # ===== Log Frame =====
        log_frame = ttk.LabelFrame(self, text="Logs", padding=(GLOBAL_PADX, TOP_PADDING))
        log_frame.grid(row=4, column=0, sticky="nsew", padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.log_text_box = tk.Text(log_frame, height=12, width=70, font=FONT_ENTRY)
        self.log_text_box.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text_box.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text_box.configure(yscrollcommand=log_scroll.set)

        # Load initial values
        self.refresh_adb_devices()
        self.destination_entry.insert(0, self.controller.config.destination)

        # Bind config updates
        self.adb_device_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_config_adb())
        self.destination_entry.bind("<KeyRelease>", lambda e: self.update_config_destination())

    def log(self, text: str) -> None:
        self.log_text_box.insert("end", text + "\n")
        self.log_text_box.see("end")

    def log_thread_safe(self, text: str) -> None:
        self.controller.update_gui_thread_safe(lambda: self.log(text))

    def refresh_adb_devices(self) -> None:
        adb_devices = self.controller.adb.get_devices()
        self.device_map = {device.friendly_name: device.serial for device in adb_devices}
        self.adb_device_dropdown["values"] = list(self.device_map.keys())

        # Set selected device if in config
        for name, serial in self.device_map.items():
            if serial == self.controller.config.adb_device:
                self.adb_device_dropdown.set(name)
                break

    def update_config_adb(self):
        name = self.adb_device_dropdown.get()
        serial = self.device_map.get(name)
        if serial:
            self.controller.config.adb_device = serial
            self.controller.config.save_config()

    def update_config_destination(self):
        self.controller.config.destination = self.destination_entry.get()
        self.controller.config.save_config()

    def back_photos(self) -> None:
        self.controller.update_gui_thread_safe(lambda: self.start_button.config(state="disabled"))
        self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(5))
        self.controller.update_gui_thread_safe(lambda: self.log_text_box.delete("1.0", "end"))

        self.log_thread_safe("Begin!")

        now = time.strftime("%Y-%m-%d_%H-%M-%S")
        folder_path = Path(".", f".temp_{now}")
        os.mkdir(folder_path)

        self.log_thread_safe("\nScanning device...")
        scan_device(self.controller.config, self.controller.adb, folder_path, self.log_thread_safe)
        self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(33 if self.controller.config.set_time else 50))

        if self.controller.config.set_time:
            self.log_thread_safe("\nSetting photo time in EXIF...")
            set_photos_exif_time(folder_path, self.log_thread_safe)
            self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(67))

        self.log_thread_safe("\nMoving to destination...")
        move(folder_path, Path(self.controller.config.destination), now, self.log_thread_safe)
        self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(100))

        if self.controller.config.delete_temporary_files:
            self.log_thread_safe("\nRemoving temporary files...")
            shutil.rmtree(folder_path)

        self.log_thread_safe("\nComplete!")
        self.controller.update_gui_thread_safe(lambda: self.start_button.config(state="active"))


class OptionsPage(ttk.Frame):
    """Settings page for configuration."""

    def __init__(self, parent: ttk.Widget, controller: BackPhotoApp):
        super().__init__(parent)
        self.controller = controller

        # ===== Ignored Directories =====
        ttk.Label(self, text="Directories to ignore:", font=FONT_LABEL).grid(row=0, column=0, sticky="w", padx=GLOBAL_PADX, pady=(TOP_PADDING, GROUPED_PADDING))
        self.ignored_dirs_text_box = tk.Text(self, height=7, font=FONT_ENTRY)
        self.ignored_dirs_text_box.grid(row=1, column=0, sticky="ew", padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))

        # ===== File Types =====
        ttk.Label(self, text="File types to move:", font=FONT_LABEL).grid(row=2, column=0, sticky="w", padx=GLOBAL_PADX, pady=(0, GROUPED_PADDING))
        self.file_ext_text_box = tk.Text(self, height=7, font=FONT_ENTRY)
        self.file_ext_text_box.grid(row=3, column=0, sticky="ew", padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))

        # ===== Checkboxes =====
        self.set_time_checkbox_var = tk.BooleanVar(value=controller.config.set_time)
        ttk.Checkbutton(self, text="Set photo time in EXIF", variable=self.set_time_checkbox_var, command=self.update_set_time).grid(
            row=4, column=0, sticky="w", padx=GLOBAL_PADX, pady=(0, GROUPED_PADDING)
        )

        self.include_dot_checkbox_var = tk.BooleanVar(value=controller.config.include_dot)
        ttk.Checkbutton(self, text="Include files/folders starting with '.'", variable=self.include_dot_checkbox_var, command=self.update_include_dot).grid(
            row=5, column=0, sticky="w", padx=GLOBAL_PADX, pady=(0, GROUPED_PADDING)
        )

        self.move_files_checkbox_var = tk.BooleanVar(value=controller.config.move_files)
        ttk.Checkbutton(self, text="Move files (instead of copying)", variable=self.move_files_checkbox_var, command=self.toggle_move_files).grid(
            row=6, column=0, sticky="w", padx=GLOBAL_PADX, pady=(0, GROUPED_PADDING)
        )

        self.checkbox_warning_label = ttk.Label(self, text="⚠️ Copying files may cause duplicates", foreground="red", wraplength=350)
        self.checkbox_warning_label.grid(row=7, column=0, sticky="w", padx=GLOBAL_PADX, pady=(0, GROUPED_PADDING))
        self.toggle_move_files()

        self.delete_temporary_files_checkbox_var = tk.BooleanVar(value=controller.config.delete_temporary_files)
        ttk.Checkbutton(self, text="Remove temporary files on completion", variable=self.delete_temporary_files_checkbox_var, command=self.update_delete_temp).grid(
            row=8, column=0, sticky="w", padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING)
        )

        # ===== Back Button =====
        ttk.Button(self, text="Back", command=lambda: controller.notebook.select(controller.start_page)).grid(
            row=9, column=0, sticky="w", padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING)
        )

        # Load initial text values
        self.ignored_dirs_text_box.insert("1.0", "\n".join(controller.config.ignored_dirs))
        self.file_ext_text_box.insert("1.0", "\n".join(controller.config.file_types))

        # Bind text changes
        self.ignored_dirs_text_box.bind("<KeyRelease>", lambda e: self.update_ignored_dirs())
        self.file_ext_text_box.bind("<KeyRelease>", lambda e: self.update_file_types())

    def toggle_move_files(self):
        if self.move_files_checkbox_var.get():
            self.checkbox_warning_label.grid_remove()
        else:
            self.checkbox_warning_label.grid()

    # ===== Update Config Methods =====
    def update_ignored_dirs(self):
        self.controller.config.ignored_dirs = [Path(path).as_posix() for path in self.ignored_dirs_text_box.get("1.0", "end").splitlines()]
        self.controller.config.save_config()

    def update_file_types(self):
        self.controller.config.file_types = [ext.lower() for ext in self.file_ext_text_box.get("1.0", "end").splitlines()]
        self.controller.config.save_config()

    def update_set_time(self):
        self.controller.config.set_time = self.set_time_checkbox_var.get()
        self.controller.config.save_config()

    def update_include_dot(self):
        self.controller.config.include_dot = self.include_dot_checkbox_var.get()
        self.controller.config.save_config()

    def update_delete_temp(self):
        self.controller.config.delete_temporary_files = self.delete_temporary_files_checkbox_var.get()
        self.controller.config.save_config()


if __name__ == "__main__":
    app = BackPhotoApp()
    app.mainloop()
