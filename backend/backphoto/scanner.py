import os
import shutil
from pathlib import Path, PurePosixPath
from typing import Callable

from .adb import ADB, DevicePath
from .config_manager import ConfigManager

TEMP_FOLDER = "temp"
ROOT_DIR = PurePosixPath("/sdcard")


def move2(src: str, dest: str) -> None:
    """Move a file while preserving metadata.

    Args:
        src (str): Source file.
        dest (str): Destination file.
    """
    shutil.copy2(src, dest)
    os.remove(src)


def get_resolved_path(wanted_filename: Path) -> Path:
    """Generate a unique filename at the same path if the given filename already exists in the directory.

    Args:
        wanted_filename (Path): Wanted filename in directory.

    Returns:
        Path: Filename allowed in directory to avoid collisions.
    """
    base_name, ext = wanted_filename.stem, wanted_filename.suffix
    counter = 1
    new_filename = wanted_filename.name

    # Increase counter until the filename is accepted
    while (wanted_filename.parent / new_filename).exists():
        new_filename = f"{base_name}_{counter}{ext}"
        counter += 1

    return wanted_filename.parent / new_filename


def scan_folder(path: DevicePath, config: ConfigManager, destination: Path, log: Callable[[str], None] | None = print) -> None:
    """Recursively scan a folder and copy/move files based on the configuration given.

    Args:
        path (DevicePath): The devices file path representing this folder.
        config (ConfigManager): The configuration to use when scanning.
        destination (str): The destination folder to place our copied/moved files into.
        log (Callable[[str], None], optional): Logging function to display messages. Defaults to print.
    """
    # Skip if we should ignore this path
    if path._path in [PurePosixPath(ignored_path) for ignored_path in config.ignored_dirs]:
        return

    if log is not None:
        log(f'Scanning: "{path.path}"')

    # Iterate though every item in the ADB folder
    for item in path.list():
        # Skip if item starts with '.' and we should ignore these
        if not config.include_dot and item.name.startswith("."):
            continue

        if item.is_dir:
            # If item is a folder then recursively call this function to scan though all files.
            scan_folder(item, config, destination, log)
        else:
            ext = item.suffix.lower()
            # Skip if we should not copy/move this type of file
            if ext not in config.file_types:
                continue

            # Ensure we have a unique filename
            resolved_destination = get_resolved_path(destination / item.name)
            item.cut2(resolved_destination) if config.move_files else item.copy2(resolved_destination)

            if log and item.name != resolved_destination.name:
                log(f'Renamed: "{item.name}" to "{resolved_destination.name}"')


def scan_device(config: ConfigManager, adb: ADB, location: Path, log: Callable[[str], None] | None = print):
    """Scan an ADB device and copy/move its files based on the configuration given.

    Args:
        config (ConfigManager): The configuration to use when selecting ADB device and scanning.
        adb (ADB): The connected adb server.
        location (Path): The destination folder to place our copied/moved files into.
        log (Callable[[str], None], optional): Logging function to display messages. Defaults to print.
    """
    adb_devices = adb.get_devices()

    for device in adb_devices:
        # Skip until we reach the correct ADB device
        if device.serial != config.adb_device:
            continue

        root = DevicePath(device, ROOT_DIR)
        scan_folder(root, config, location, log)
        break
