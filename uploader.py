import os
import shutil

import photo_tools

MONTH_NAMES = ["01January", "02February", "03March", "04April", "05May", "06June", "07July", "08August", "09September", "10October", "11November", "12December"]


def upload(local_path, remote_path, last_updated=None):
    os.makedirs(os.path.dirname(remote_path), exist_ok=True)

    for root, dirs, files in os.walk(local_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            time = photo_tools.GetOSTime(file_path)
            remote_file_path = os.path.join(remote_path, str(time.year), MONTH_NAMES[time.month], filename)
            os.makedirs(os.path.dirname(remote_file_path), exist_ok=True)
            shutil.copy2(file_path, remote_file_path)

    if last_updated:
        with open(os.path.join(remote_path, "LastUpdated.txt"), "w") as f:
            f.write(last_updated)
