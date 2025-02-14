import os
import shutil

import win32com.client

shell = win32com.client.Dispatch("Shell.Application")
TEMP_FOLDER = "temp"


def move2(src, dest):
    """Move a file while preserving metadata."""
    shutil.copy2(src, dest)
    os.remove(src)


def get_mtp_devices():
    mtp_devices = shell.Namespace(17)  # 17 corresponds to "This PC" in Windows

    return mtp_devices.Items()


def get_resolved_filename(filename, directory):
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base_name}_{counter}{ext}"
        counter += 1

    return new_filename


def scan_folder(path, folder, config, destination, log=print):
    if path in config.ignored_dirs:
        return

    log(f"Scanning: {path}")

    for item in folder.Items():
        if not config.include_dot and item.Name.startswith("."):
            continue

        if item.IsFolder:
            scan_folder(os.path.join(path, item.Name), item.GetFolder, config, destination, log)
        else:
            ext = os.path.splitext(item.Name)[1].lower()
            if ext in config.file_types:
                new_filename = get_resolved_filename(item.Name, destination)
                if item.Name == new_filename:
                    destination_shell = shell.Namespace(destination)
                    destination_shell.MoveHere(item) if config.move_files else destination_shell.CopyHere(item)
                else:
                    temp_destination = os.path.join(destination, TEMP_FOLDER)
                    os.mkdir(temp_destination)
                    temp_destination_shell = shell.Namespace(temp_destination)
                    temp_destination_shell.MoveHere(item) if config.move_files else temp_destination_shell.CopyHere(item)
                    move2(os.path.join(temp_destination, item.Name), os.path.join(destination, new_filename))

                    log(f"Renamed {item.Name} to {new_filename}")


def scan_device(config, location, log=print):
    mtp_devices = get_mtp_devices()

    for device in mtp_devices:
        if device.Name != config.mtp_device:
            continue

        scan_folder("", device.GetFolder, config, location, log)
