import os
import shutil
from pathlib import Path, PurePosixPath
from typing import Generator

from adb import ADB, DevicePath
from fastapi import HTTPException
from server import ADB_NO_CONNECTION
from typings import BackupYield, LogEntry, UserConfig

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


def scan_folder(
    path: DevicePath, config: UserConfig, destination: Path, depth: int = 0, passed_progress: float = 0, progress_multiplier: float = 1
) -> Generator[BackupYield, None, None]:
    """Recursively scan a folder and copy/move files based on the configuration given.

    Args:
        path (DevicePath): The devices file path representing this folder.
        config (ConfigManager): The configuration to use when scanning.
        destination (str): The destination folder to place our copied/moved files into.
    """
    # Skip if we should ignore this path
    if path._path in [PurePosixPath(ignored_path) for ignored_path in config.ignoredDirs]:
        return

    yield BackupYield(log=LogEntry(content=f"Scanning {path.path}"))

    # Iterate though every item in the ADB folder
    items = path.list()

    # Skip if item starts with '.' and we should ignore these
    if config.skipDot:
        items = [item for item in items if not item.name.startswith(".")]
    total_item_count = len(items)

    for i, item in enumerate(items):
        if item.is_dir:
            # If item is a folder then recursively call this function to scan though all files.
            yield from scan_folder(
                item, config, destination, depth + 1, passed_progress + (i / total_item_count) * progress_multiplier, progress_multiplier * (1 / total_item_count)
            )
        else:
            ext = item.suffix.lower()
            # Skip if we should not copy/move this type of file
            if ext not in config.fileTypes:
                continue

            # Ensure we have a unique filename
            resolved_destination = get_resolved_path(destination / item.name)
            item.cut2(resolved_destination) if config.moveFiles else item.copy2(resolved_destination)

            if item.name != resolved_destination.name:
                yield BackupYield(log=LogEntry(content=f"Renamed {item.name} to {resolved_destination.name}"))

        if depth < 2:
            yield BackupYield(progress=(passed_progress + ((i + 1) / total_item_count) * progress_multiplier))


def scan_device(location: Path, adb: ADB, config: UserConfig) -> Generator[BackupYield, None, None]:
    """Scan an ADB device and copy/move its files based on the configuration given.

    Args:
        location (Path): The destination folder to place our copied/moved files into.
        adb (ADB): The connected adb server.
        config (UserConfig): The configuration to use when selecting ADB device and scanning.
    """
    if config.adbDevice is None:
        raise Exception("Device not selected")

    try:
        device = adb.get_device(config.adbDevice)
    except:
        raise HTTPException(status_code=ADB_NO_CONNECTION, detail="Could not connect to ADB server")

    if device is None:
        raise Exception("ADB device not found")

    if not device.authorised:
        raise Exception("Device is not authorised for ADB")

    root = DevicePath(device, ROOT_DIR)
    try:
        yield from scan_folder(root, config, location)
    except:
        if adb.is_alive():
            raise Exception("ADB device was disconnected")
        else:
            raise HTTPException(status_code=ADB_NO_CONNECTION, detail="Could not connect to ADB server")
