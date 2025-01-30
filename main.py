import tkinter as tk
from tkinter import messagebox, ttk


def start():
    messagebox.showinfo(f"{mtp_device_dropdown.get()}, {set_time_checkbox_var.get()}")

root = tk.Tk()
root.title("backPhoto")
root.geometry("800x600")

mtp_device_dropdown_label = tk.Label(root, text="Select an MTP Device:")
mtp_device_dropdown_label.pack(pady=5)

mtp_device_dropdown = ttk.Combobox(root, values=["Device 1", "Device 2", "Device 3"])
mtp_device_dropdown.pack(pady=5)
mtp_device_dropdown.set("Device 1")  # Default selection

# todo add list of ignored directories
# todo add list of included file extensions

set_time_checkbox_var = tk.BooleanVar()
set_time_checkbox = tk.Checkbutton(root, text="Set photo time in EXIF", variable=set_time_checkbox_var)
set_time_checkbox.pack(pady=5)

start_button = tk.Button(root, text="Start", command=start)
start_button.pack(pady=10)

root.mainloop()
