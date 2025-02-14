import os
import shutil
from typing import Callable, Optional

import photo_tools

MONTH_NAMES = ["01January", "02February", "03March", "04April", "05May", "06June", "07July", "08August", "09September", "10October", "11November", "12December"]


def upload(local_path: str, remote_path: str, last_updated: Optional[str] = None, log: Optional[Callable[[str], None]] = print) -> None:
    """Uploads files from a local directory to a remote directory, organising them by year and month.

    Args:
        local_path (str): The source directory containing the files to upload.
        remote_path (str): The destination directory for the uploaded files.
        last_updated (Optional[str], optional): A timestamp to write to a LastUpdated.txt file. Defaults to None.
        log (Optional[Callable[[str], None]], optional): Logging function to display messages. Defaults to print.
    """
    # Ensure the remote path exists
    os.makedirs(os.path.dirname(remote_path), exist_ok=True)

    # Iterate though every file in `local_path`
    for root, dirs, files in os.walk(local_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Organise file into year and month folders
            time = photo_tools.get_os_time(file_path)
            remote_file_path = os.path.join(remote_path, str(time.year), MONTH_NAMES[time.month], filename)

            # Copy the file with metadata to the organised location in the remote path
            os.makedirs(os.path.dirname(remote_file_path), exist_ok=True)
            shutil.copy2(file_path, remote_file_path)

            log(f'Uploaded: "{os.path.basename(file_path)}"')

    # If a last updated text is given then write this into the remote path
    if last_updated:
        with open(os.path.join(remote_path, "LastUpdated.txt"), "w") as f:
            f.write(last_updated)

        log(f'Uploaded: "{"LastUpdated.txt"}"')
