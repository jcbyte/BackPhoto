import os

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
                destination.MoveHere(item) if config.move_files else destination.CopyHere(item)


def scan_device(config, location, log):
    mtp_devices = get_mtp_devices()
    destination = shell.Namespace(location)

    for device in mtp_devices:
        if device.Name != config.mtp_device:
            continue

        scan_folder("", device.GetFolder, config, destination, log)
