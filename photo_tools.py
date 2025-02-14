import os
from datetime import datetime
from typing import Any, Dict, Optional

import piexif
from PIL import Image

IMAGE_FORMAT = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".svg", ".ico"]


def get_os_time(path: str) -> datetime:
    """Returns the last modified time of a file as a datetime object.

    Args:
        path (str): The file path.

    Returns:
        datetime: Time of the files last modification.
    """
    return datetime.fromtimestamp(os.path.getmtime(path))


def convert_to_jpg(path: str) -> str:
    """Converts an image to JPG format, and removes the original file

    Args:
        path (str): The file path of the image to convert.

    Returns:
        str: The new file path of the converted JPG image.

    Raises:
        ValueError: If the image contains transparency.
    """
    name, ext = os.path.splitext(path)

    # Check that the file is not already a JPG
    if ext.lower() in [".jpg", ".jpeg"]:
        return path

    img = Image.open(path)

    # If the image has transparency then raise error
    min_alpha = img.convert("RGBA").getextrema()[-1][0]
    if min_alpha < 255:
        raise ValueError("Image contains transparency")

    # Convert and save image as JGP
    img_rgb = img.convert("RGB")
    new_path = f"{name}.jpg"
    img_rgb.save(new_path)

    # Remove the original file
    os.remove(path)

    return new_path


def load_exif(path: str) -> Optional[Dict[str, Any]]:
    """Loads the EXIF data from an image file.

    Args:
        path (str): The file path of the image.

    Returns:
        Optional[Dict[str, Any]]: The EXIF data as a dictionary, or None if it cannot be loaded.
    """
    try:
        return piexif.load(path)
    except:
        return None


def save_exif(exif: Dict[str, Any], path: str) -> None:
    """Saves EXIF data to an image file.

    Args:
        exif (Dict[str, Any]): The EXIF data to save.
        path (str): The file path of the image.
    """
    exif_bytes = piexif.dump(exif)
    piexif.insert(exif_bytes, path)


def validate_exif_time(exif: Dict[str, Any]) -> bool:
    """Validates if the EXIF data contains necessary time fields.

    Args:
        exif (Dict[str, Any]): The EXIF data to validate.

    Returns:
        bool: True if all required time fields are present, False otherwise.
    """
    # Check all creation time based fields
    if piexif.ImageIFD.DateTime not in exif["0th"]:
        return False
    if piexif.ExifIFD.DateTimeDigitized not in exif["Exif"]:
        return False
    if piexif.ExifIFD.DateTimeOriginal not in exif["Exif"]:
        return False

    return True


def set_exif_time(exif: Dict[str, Any], time: datetime) -> None:
    """Sets the EXIF time fields to a specified datetime value.

    Args:
        exif (Dict[str, Any]): The EXIF data to update.
        time (datetime): The datetime value to set.
    """
    time = time.strftime("%Y:%m:%d %H:%M:%S")
    exif["0th"][piexif.ImageIFD.DateTime] = time
    exif["Exif"][piexif.ExifIFD.DateTimeDigitized] = time
    exif["Exif"][piexif.ExifIFD.DateTimeOriginal] = time


def set_photo_exif_time(file_path: str, log=print) -> None:
    """Sets the EXIF time of an image based on its file modification time.

    Args:
        file_path (str): The file path of the image.
        log (callable, optional): Logging function to display messages.
    """
    ext = os.path.splitext(file_path)[1].lower()

    # Check file is an image
    if ext not in IMAGE_FORMAT:
        return

    try:
        exif = load_exif(file_path)
        if exif:
            # DOnt update if EXIF time already exists
            if validate_exif_time(exif):
                return

            # If EXIF exists but no time, then just add this and save it back
            set_exif_time(exif, get_os_time(file_path))
            save_exif(exif, file_path)
        else:
            # If EXIF data does not exist create a minimal one containing time data
            exif = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
            set_exif_time(exif, get_os_time(file_path))
            # Ensure the file is a JPG and save the created EXIF data to it
            file_path = convert_to_jpg(file_path)
            save_exif(exif, file_path)

        log(f'Updated: "{os.path.basename(file_path)}"')

    except:
        log(f'Error: "{os.path.basename(file_path)}"')


def set_photos_exif_time(folder_path: str, log=print) -> None:
    """Sets or updates the EXIF time for all images in a folder.

    Args:
        folder_path (str): The path to the folder containing images.
        log (callable, optional): Logging function to display messages.
    """
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            set_photo_exif_time(file_path, log)
