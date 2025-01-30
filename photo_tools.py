import os
from datetime import datetime

IMAGE_FORMAT = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".svg", ".ico"]
JPG_FORMAT = [".jpg", ".jpeg"]


def GetOSTime(path):
    return datetime.fromtimestamp(os.path.getmtime(path))
