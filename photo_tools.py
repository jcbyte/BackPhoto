import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import piexif
from PIL import Image

IMAGE_FORMAT = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".svg", ".ico"]


def get_os_time(path: Path) -> datetime:
    """Returns the last modified time of a file as a datetime object.

    Args:
        path (Path): The file path.

    Returns:
        datetime: Time of the files last modification.
    """
    return datetime.fromtimestamp(path.stat().st_mtime)


def convert_to_jpg(path: Path) -> Path:
    """Converts an image to JPG format, and removes the original file

    Args:
        path (Path): The file path of the image to convert.

    Returns:
        Path: The new file path of the converted JPG image.

    Raises:
        ValueError: If the image contains transparency.
    """
    # todo replace path.splitext with path.stem and path.suffix
    name, ext = os.path.splitext(path.name)

    # Check that the file is not already a JPG
    if ext.lower() in [".jpg", ".jpeg"]:
        return path

    img = Image.open(path)

    # If the image has transparency then raise error
    alpha_channel = img.convert("RGBA").getchannel("A")
    min_alpha, max_alpha = alpha_channel.getextrema()
    assert isinstance(min_alpha, int)  # For type checker
    if min_alpha < 255:
        raise ValueError("Image contains transparency")

    # Convert and save image as JGP
    img_rgb = img.convert("RGB")
    new_path = path.parent / f"{name}.jpg"
    img_rgb.save(new_path)

    # Remove the original file
    path.unlink()

    return new_path


def load_exif(path: Path) -> Optional[Dict[str, Any]]:
    """Loads the EXIF data from an image file.

    Args:
        path (Path): The file path of the image.

    Returns:
        Optional[Dict[str, Any]]: The EXIF data as a dictionary, or None if it cannot be loaded.
    """
    try:
        return piexif.load(path)
    except:
        return None


def save_exif(exif: Dict[str, Any], path: Path) -> None:
    """Saves EXIF data to an image file.

    Args:
        exif (Dict[str, Any]): The EXIF data to save.
        path (Path): The file path of the image.
    """
    exif_bytes = piexif.dump(exif)
    piexif.insert(exif_bytes, path)


def get_exif_time(exif: Dict[str, Any]) -> tuple[None | datetime, bool]:
    """Gets and validates if the EXIF data contains necessary time fields.

    Args:
        exif (Dict[str, Any]): The EXIF data to use.

    Returns:
        tuple[None | datetime, bool]:
        - The date in the exif data.
        - True if all required time fields are present, False otherwise.
    """
    # Get all creation time based fields
    dt0_time: bytes | None = exif.get("0th", {}).get(piexif.ImageIFD.DateTime)
    dt_digitized_time: bytes | None = exif.get("Exif", {}).get(piexif.ExifIFD.DateTimeDigitized)
    dt_original_time: bytes | None = exif.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal)

    time = None
    time_bytes = dt0_time or dt_digitized_time or dt_original_time
    if time_bytes:
        time_str = time_bytes.decode("utf-8")
        time = datetime.strptime(time_str, "%Y:%m:%d %H:%M:%S")

    missing_fields = dt0_time is None or dt_digitized_time is None or dt_original_time is None

    return time, missing_fields


def set_exif_time(exif: Dict[str, Any], time: datetime) -> None:
    """Sets the EXIF time fields to a specified datetime value.

    Args:
        exif (Dict[str, Any]): The EXIF data to update.
        time (datetime): The datetime value to set.
    """
    time_str = time.strftime("%Y:%m:%d %H:%M:%S")
    exif["0th"][piexif.ImageIFD.DateTime] = time_str
    exif["Exif"][piexif.ExifIFD.DateTimeDigitized] = time_str
    exif["Exif"][piexif.ExifIFD.DateTimeOriginal] = time_str


def set_photo_exif_time(file_path: Path, log: Optional[Callable[[str], None]] = print) -> None:
    """Sets the EXIF time of an image based on its file modification time.

    Args:
        file_path (Path): The file path of the image.
        log (Optional[Callable[[str], None]], optional): Logging function to display messages. Defaults to print.
    """
    ext = os.path.splitext(file_path)[1].lower()

    # Check file is an image
    if ext not in IMAGE_FORMAT:
        return

    try:
        exif = load_exif(file_path)
        if exif:
            # Don't update if EXIF time already exists
            exif_time, missing_fields = get_exif_time(exif)
            if not missing_fields:
                return

            # If EXIF exists but no time, then just add this and save it back
            set_exif_time(exif, exif_time or get_os_time(file_path))
            save_exif(exif, file_path)
        else:
            # If EXIF data does not exist create a minimal one containing time data
            exif = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
            set_exif_time(exif, get_os_time(file_path))
            # Ensure the file is a JPG and save the created EXIF data to it
            file_path = convert_to_jpg(file_path)
            save_exif(exif, file_path)

        if log:
            log(f'Updated: "{os.path.basename(file_path)}"')

    except:
        if log:
            log(f'Error: "{os.path.basename(file_path)}"')


def set_photos_exif_time(folder_path: Path, log: Optional[Callable[[str], None]] = print) -> None:
    """Sets or updates the EXIF time for all images in a folder.

    Args:
        folder_path (Path): The path to the folder containing images.
        log (Optional[Callable[[str], None]], optional): Logging function to display messages. Defaults to print.
    """
    for file_path in folder_path.rglob("*"):
        # skip directories
        if file_path.is_file():
            set_photo_exif_time(file_path, log)
