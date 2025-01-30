import tkinter as tk
from tkinter import messagebox, ttk


def start():
    messagebox.showinfo("", f"{mtp_device_dropdown.get()}, {set_time_checkbox_var.get()}")

root = tk.Tk()
root.title("backPhoto")
root.geometry("800x600")

mtp_device_dropdown_label = tk.Label(root, text="Select an MTP Device:")
mtp_device_dropdown_label.pack(pady=5)
mtp_device_dropdown = ttk.Combobox(root, values=["Device 1", "Device 2", "Device 3"])
mtp_device_dropdown.pack(pady=5)
mtp_device_dropdown.set("Device 1")  # Default selection

remote_destination_entry_label = tk.Label(root, text="Enter remote destination path:")
remote_destination_entry_label.pack(pady=5)
remote_destination_entry = tk.Entry(root, width=50)
remote_destination_entry.pack(pady=5)

ignored_dirs_text_box_label = tk.Label(root, text="Enter directories to ignore (each on newline):")
ignored_dirs_text_box_label.pack(pady=5)
ignored_dirs_text_box = tk.Text(root, height=5, width=50)
ignored_dirs_text_box.pack(pady=5)

file_ext_text_box_label = tk.Label(root, text="Enter file extensions to move (each on newline):")
file_ext_text_box_label.pack(pady=5)
file_ext_text_box_label = tk.Text(root, height=5, width=50)
file_ext_text_box_label.pack(pady=5)

set_time_checkbox_var = tk.BooleanVar()
set_time_checkbox = tk.Checkbutton(root, text="Set photo time in EXIF", variable=set_time_checkbox_var)
set_time_checkbox.pack(pady=5)

include_dot_checkbox_var = tk.BooleanVar()
include_dot_checkbox = tk.Checkbutton(root, text="Include files and folders starting with a '.'", variable=include_dot_checkbox_var)
include_dot_checkbox.pack(pady=5)

start_button = tk.Button(root, text="Start", command=start)
start_button.pack(pady=10)

root.mainloop()
