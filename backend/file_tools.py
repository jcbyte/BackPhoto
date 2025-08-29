import os
import shutil
from pathlib import Path
from typing import Callable, Generator

from photo_tools import get_exif_time, get_os_time, load_exif
from typings import BackupYield, LogEntry

MONTH_NAMES = ["01January", "02February", "03March", "04April", "05May", "06June", "07July", "08August", "09September", "10October", "11November", "12December"]


def move(src: Path, dst: Path, last_updated: str | None = None) -> Generator[BackupYield, None, None]:
    """Moves files from a source directory to a destination directory, organising them by year and month.

    Args:
        local_path (Path): The source directory containing the files to upload.
        remote_path (Path): The destination directory for the uploaded files.
        last_updated (str, optional): A timestamp to write to a LastUpdated.txt file. Defaults to None.
    """
    # Ensure the remote path exists
    dst.mkdir(parents=True, exist_ok=True)

    # Iterate through every file in source directory
    for file_path in src.rglob("*"):  # recursively find all files
        if file_path.is_file():
            # Organise file into year and month folders
            photo_exif = load_exif(file_path)
            exif_time = get_exif_time(photo_exif)[0] if photo_exif else None
            time = exif_time or get_os_time(file_path)

            dst_path = dst / str(time.year) / MONTH_NAMES[time.month - 1] / file_path.name

            # Ensure the parent directories exist
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file with metadata
            shutil.copy2(file_path, dst_path)

            # yield BackupYield(log=LogEntry(content=f'Uploaded: "{file_path.name}"'))

    # If a last updated text is given then write this into the remote path
    if last_updated:
        with open(os.path.join(dst, "LastUpdated.txt"), "w") as f:
            f.write(last_updated)

        yield BackupYield(log=LogEntry(content="Set LastUpdated.txt"))
