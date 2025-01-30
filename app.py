import os
import time
import tkinter as tk
from tkinter import messagebox, ttk

import config_manager
import scanner

TOP_PADDING = 10
GROUPED_PADDING = 2
SEPARATED_PADDING = 15
GLOBAL_PADX = 5


class BackPhotoApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.config = config_manager.ConfigManager("./config.json")

        self.title("backPhoto")
        self.geometry("800x600")

        self.current_frame = None
        self.frames = {}
        for Page in [StartPage, OptionsPage]:
            page_name = Page.__name__
            frame = Page(parent=self, controller=self)
            self.frames[page_name] = frame

        self.switch_page("StartPage")

    def switch_page(self, page_name):
        if self.current_frame:
            self.current_frame.place_forget()

        frame = self.frames[page_name]
        frame.place(relx=0.5, rely=0, anchor="n")
        self.current_frame = frame


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ## GUI Elements ##

        # MTP Device Dropdown
        tk.Label(self, text="MTP Device:").grid(row=0, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(TOP_PADDING, GROUPED_PADDING))
        self.mtp_device_dropdown = ttk.Combobox(self, state="readonly")
        self.mtp_device_dropdown.grid(row=1, column=0, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Refresh Button
        self.mtp_device_refresh_button = tk.Button(self, text="Refresh", command=self.refresh_mtp_devices)
        self.mtp_device_refresh_button.grid(row=1, column=1, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Remote Destination Entry
        tk.Label(self, text="Remote destination path:").grid(row=2, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(0, GROUPED_PADDING))
        self.remote_destination_entry = tk.Entry(self, width=50)
        self.remote_destination_entry.grid(row=3, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Options Button
        self.options_button = tk.Button(self, text="Options", command=lambda: controller.switch_page("OptionsPage"), width=15)
        self.options_button.grid(row=4, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))

        # Start Button
        self.start_button = tk.Button(self, text="Start", command=self.start, width=25)
        self.start_button.grid(row=5, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))

        ## Load Initial Values ##

        self.refresh_mtp_devices()

        if self.controller.config.mtp_device in self.mtp_device_dropdown["values"]:
            self.mtp_device_dropdown.set(self.controller.config.mtp_device) 
        self.remote_destination_entry.insert(0, self.controller.config.remote_destination)

        ## Config Callbacks ##

        def update_mtp_device():
            self.controller.config.mtp_device = self.mtp_device_dropdown.get()
            self.controller.config.save_config()

        self.mtp_device_dropdown.bind("<<ComboboxSelected>>", lambda *_: update_mtp_device())

        def update_remote_destination():
            self.controller.config.remote_destination = self.remote_destination_entry.get()
            self.controller.config.save_config()

        self.remote_destination_entry.bind("<KeyRelease>", lambda *_: update_remote_destination())

    def refresh_mtp_devices(self):
        mtp_devices = scanner.get_mtp_devices()
        self.mtp_device_dropdown["values"] = [device.Name for device in mtp_devices]

    def start(self):
        # todo show output
        # todo threading to stop

        # Create temporary working folder
        now = time.strftime('%Y-%m-%d_%H-%M-%S')
        folder_path = os.path.abspath(f"./.temp_{now}")
        os.mkdir(folder_path)

        # Find and move/copy all photos from MTP device to working folder
        scanner.scan_device(self.controller.config, folder_path)

        # todo modify EXIF if required
        # todo upload to remote destination

        # messagebox.showinfo("", f"Run")


class OptionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ## GUI Elements ##

        # Ignored Directories Text Box
        tk.Label(self, text="Directories to ignore (each on a newline):").grid(row=0, column=0, padx=GLOBAL_PADX, pady=(TOP_PADDING, GROUPED_PADDING))
        self.ignored_dirs_text_box = tk.Text(self, height=7, width=50)
        self.ignored_dirs_text_box.grid(row=1, column=0, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Included File Extensions Text Box
        tk.Label(self, text="File types to move (each on a newline):").grid(row=2, column=0, padx=GLOBAL_PADX, pady=(0, GROUPED_PADDING))
        self.file_ext_text_box = tk.Text(self, height=7, width=50)
        self.file_ext_text_box.grid(row=3, column=0, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Set Time Checkbox
        self.set_time_checkbox_var = tk.BooleanVar()
        self.set_time_checkbox = tk.Checkbutton(self, text="Set photo time in EXIF", variable=self.set_time_checkbox_var)
        self.set_time_checkbox.grid(row=4, column=0, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Include Dot Files Checkbox
        self.include_dot_checkbox_var = tk.BooleanVar()
        self.include_dot_checkbox = tk.Checkbutton(self, text="Include files and folders starting with a '.'", variable=self.include_dot_checkbox_var)
        self.include_dot_checkbox.grid(row=5, column=0, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Move Files Checkbox
        self.move_files_checkbox_var = tk.BooleanVar()
        self.move_files_checkbox = tk.Checkbutton(self, text="Move files (instead of copying them)", variable=self.move_files_checkbox_var)
        self.move_files_checkbox.grid(row=6, column=0, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Back Button
        self.back_button = tk.Button(self, text="Back", command=lambda: controller.switch_page("StartPage"), width=15)
        self.back_button.grid(row=7, column=0, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))

        ## Load Initial Values ##

        self.ignored_dirs_text_box.insert("1.0", "\n".join(self.controller.config.ignored_dirs))
        self.file_ext_text_box.insert("1.0", "\n".join(self.controller.config.file_types))
        self.set_time_checkbox_var.set(self.controller.config.set_time)
        self.include_dot_checkbox_var.set(self.controller.config.include_dot)
        self.move_files_checkbox_var.set(self.controller.config.move_files)

        ## Config Callbacks ##

        def update_ignored_dirs():
            self.controller.config.ignored_dirs = [os.path.normpath(path) for path in self.ignored_dirs_text_box.get("1.0", "end").splitlines()]
            self.controller.config.save_config()

        self.ignored_dirs_text_box.bind("<KeyRelease>", lambda *_: update_ignored_dirs())

        def update_file_types():
            self.controller.config.file_types = [ext.lower() for ext in self.file_ext_text_box.get("1.0", "end").splitlines()]
            self.controller.config.save_config()

        self.file_ext_text_box.bind("<KeyRelease>", lambda *_: update_file_types())

        def update_set_time():
            self.controller.config.set_time = self.set_time_checkbox_var.get()
            self.controller.config.save_config()

        self.set_time_checkbox_var.trace_add("write", lambda *_: update_set_time())

        def update_include_dot():
            self.controller.config.include_dot = self.include_dot_checkbox_var.get()
            self.controller.config.save_config()

        self.include_dot_checkbox_var.trace_add("write", lambda *_: update_include_dot())

        def update_move_files():
            self.controller.config.move_files = self.move_files_checkbox_var.get()
            self.controller.config.save_config()

        self.move_files_checkbox_var.trace_add("write", lambda *_: update_move_files())


if __name__ == "__main__":
    app = BackPhotoApp()
    app.mainloop()
