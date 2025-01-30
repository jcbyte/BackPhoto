import tkinter as tk
from tkinter import messagebox, ttk

TOP_PADDING = 10
GROUPED_PADDING = 2
SEPARATED_PADDING = 15
GLOBAL_PADX = 5

class BackPhotoApp(tk.Tk):
    def __init__(self):
        super().__init__()

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

        # MTP Device Dropdown
        tk.Label(self, text="MTP Device:").grid(row=0, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(TOP_PADDING, GROUPED_PADDING))
        self.mtp_device_dropdown = ttk.Combobox(self, values=["Device 1", "Device 2", "Device 3"])
        self.mtp_device_dropdown.grid(row=1, column=0, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Refresh Button
        self.mtp_device_refresh_button = tk.Button(self, text="Refresh")
        self.mtp_device_refresh_button.grid(row=1, column=1, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Remote Destination Entry
        tk.Label(self, text="Remote destination path:").grid(row=2, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(0, GROUPED_PADDING))
        self.remote_destination_entry = tk.Entry(self, width=50)
        self.remote_destination_entry.grid(row=3, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING), sticky="nsew")

        # Options Button
        self.options_button = tk.Button(self, text="Options", command=lambda: controller.switch_page("OptionsPage"), width=25)
        self.options_button.grid(row=4, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))

        # Start Button
        self.start_button = tk.Button(self, text="Start", command=self.start, width=25)
        self.start_button.grid(row=5, column=0, columnspan=2, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))

    def start(self):
        """Handles the Start button click event."""
        messagebox.showinfo("", f"{self.mtp_device_dropdown.get()}, {self.remote_destination_entry.get()}")


class OptionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

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

        # Back Button
        self.back_button = tk.Button(self, text="Back", command=lambda: controller.switch_page("StartPage"), width=25)
        self.back_button.grid(row=6, column=0, padx=GLOBAL_PADX, pady=(0, SEPARATED_PADDING))


if __name__ == "__main__":
    app = BackPhotoApp()
    app.mainloop()
