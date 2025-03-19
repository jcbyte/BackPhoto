import os
import shutil
import time
from typing import Callable, Iterator, Optional

# ! win32com.client does not have typing hints
import win32com.client

from config_manager import ConfigManager

shell = win32com.client.Dispatch("Shell.Application")
TEMP_FOLDER = "temp"


def move2(src: str, dest: str) -> None:
    """Move a file while preserving metadata.

    Args:
        src (str): Source file.
        dest (str): Destination file.
    """
    shutil.copy2(src, dest)
    os.remove(src)


def wait_for_file_exists(path: str, timeout: float = 60, poll: float = 0.01) -> bool:
    start_time = time.time()

    while not os.path.exists(path):
        if time.time() - start_time >= timeout:
            return False

        time.sleep(poll)

    return True


def get_mtp_devices() -> any:
    """Retrieve a list of MTP devices connected to thew windows system.

    Returns:
        any: List of MTP devices
    """
    mtp_devices = shell.Namespace(17)  # 17 corresponds to "This PC" in Windows

    return mtp_devices.Items()


def get_resolved_filename(filename: str, directory: str) -> str:
    """Generate a unique filename if the given filename already exists in the directory.

    Args:
        filename (str): Wanted filename.
        directory (str): Directory path.

    Returns:
        str: Filename allowed in directory to avoid collisions.
    """
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    # Increase counter until the filename is accepted
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base_name}_{counter}{ext}"
        counter += 1

    return new_filename


def scan_folder(path: str, folder: any, config: ConfigManager, destination: str, log: Optional[Callable[[str], None]] = print) -> None:
    """Recursively scan a folder and copy/move files based on the configuration given.

    Args:
        path (str): The "file path" representing this folder.
        folder (any): The MTP device folder
        config (ConfigManager): The configuration to use when scanning.
        destination (str): The destination folder to place our copied/moved files into.
        log (Optional[Callable[[str], None]], optional): Logging function to display messages. Defaults to print.
    """
    # Skip if we should ignore this path
    if path in config.ignored_dirs:
        return

    log(f'Scanning: "{path}"')

    # Iterate though every item in the MTP folder
    for item in folder.Items():
        # Skip if item starts with '.' and we should ignore these
        if not config.include_dot and item.Name.startswith("."):
            continue

        if item.IsFolder:
            # If item is a folder then recursively call this function to scan though all files.
            scan_folder(os.path.join(path, item.Name), item.GetFolder, config, destination, log)
        else:
            ext = os.path.splitext(item.Name)[1].lower()
            # Skip if we should not copy/move this type of file
            if ext not in config.file_types:
                continue

            new_filename = get_resolved_filename(item.Name, destination)
            if item.Name == new_filename:
                # If there is no name conflicts then copy/move this file into the destination folder
                destination_shell = shell.Namespace(destination)
                destination_shell.MoveHere(item) if config.move_files else destination_shell.CopyHere(item)
                # Shell.Application functions are asynchronous, so wait for the file to actually be moved
                if not wait_for_file_exists(destination, timeout=5 * 60):
                    log(f'Issue {'Moving' if config.move_files else 'Coping'} "{item.Name}"')
            else:
                # If there are name conflicts then first copy/move the file into a temporary directory and then move it into the main directory
                # We must do this as win32com.client cannot copy/move directly to a different filename
                temp_destination = os.path.join(destination, TEMP_FOLDER)
                os.makedirs(temp_destination, exist_ok=True)

                temp_destination_shell = shell.Namespace(temp_destination)
                temp_destination_shell.MoveHere(item) if config.move_files else temp_destination_shell.CopyHere(item)
                # Shell.Application functions are asynchronous, so wait for the file to actually be moved
                if not wait_for_file_exists(temp_destination, timeout=5 * 60):
                    log(f'Issue {'Moving' if config.move_files else 'Coping'} "{item.Name}"')

                move2(os.path.join(temp_destination, item.Name), os.path.join(destination, new_filename))

                log(f'Renamed: "{item.Name}" to "{new_filename}"')


def scan_device(config: ConfigManager, location: str, log: Optional[Callable[[str], None]] = print):
    """Scan an MTP device and copy/move its files based on the configuration given.

    Args:
        config (ConfigManager): The configuration to use when selecting MTP device and scanning.
        location (str): The destination folder to place our copied/moved files into.
        log (Optional[Callable[[str], None]], optional): Logging function to display messages. Defaults to print.
    """
    mtp_devices = get_mtp_devices()

    for device in mtp_devices:
        # Skip until we reach the correct MTP device
        if device.Name != config.mtp_device:
            continue

        scan_folder("", device.GetFolder, config, location, log)
