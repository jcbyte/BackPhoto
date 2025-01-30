import tkinter as tk
from tkinter import messagebox, ttk


class BackPhotoApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("backPhoto")
        self.geometry("800x600")

        self.frames = {}
        for Page in [StartPage, OptionsPage]:
            page_name = Page.__name__
            frame = Page(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.switch_page("StartPage")

    def switch_page(self, page_name):
        """Bring the selected page to the front"""
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # MTP Device Dropdown
        tk.Label(self, text="Select an MTP Device:").pack(pady=5)
        self.mtp_device_dropdown = ttk.Combobox(self, values=["Device 1", "Device 2", "Device 3"])
        self.mtp_device_dropdown.pack(pady=5)
        self.mtp_device_dropdown.set("Device 1")  # Default selection

        # Remote Destination Entry
        tk.Label(self, text="Enter remote destination path:").pack(pady=5)
        self.remote_destination_entry = tk.Entry(self, width=50)
        self.remote_destination_entry.pack(pady=5)

        # Options Button
        self.options_button = tk.Button(self, text="Options", command=lambda: controller.show_frame("OptionsPage"))
        self.options_button.pack(pady=10)

        # Start Button
        self.start_button = tk.Button(self, text="Start", command=self.start)
        self.start_button.pack(pady=10)

    def start(self):
        """Handles the Start button click event."""
        messagebox.showinfo("", f"{self.mtp_device_dropdown.get()}, {self.set_time_checkbox_var.get()}")


class OptionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Ignored Directories Text Box
        tk.Label(self, text="Enter directories to ignore (each on newline):").pack(pady=5)
        self.ignored_dirs_text_box = tk.Text(self, height=5, width=50)
        self.ignored_dirs_text_box.pack(pady=5)

        # Included File Extensions Text Box
        tk.Label(self, text="Enter file extensions to move (each on newline):").pack(pady=5)
        self.file_ext_text_box = tk.Text(self, height=5, width=50)
        self.file_ext_text_box.pack(pady=5)

        # Set Time Checkbox
        self.set_time_checkbox_var = tk.BooleanVar()
        self.set_time_checkbox = tk.Checkbutton(self, text="Set photo time in EXIF", variable=self.set_time_checkbox_var)
        self.set_time_checkbox.pack(pady=5)

        # Include Dot Files Checkbox
        self.include_dot_checkbox_var = tk.BooleanVar()
        self.include_dot_checkbox = tk.Checkbutton(self, text="Include files and folders starting with a '.'", variable=self.include_dot_checkbox_var)
        self.include_dot_checkbox.pack(pady=5)

        # Back Button
        self.back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("StartPage"))
        self.back_button.pack(pady=10)


if __name__ == "__main__":
    app = BackPhotoApp()
    app.mainloop()
