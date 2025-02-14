import os
from datetime import datetime

import piexif
from PIL import Image

IMAGE_FORMAT = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".svg", ".ico"]


def get_os_time(path):
    return datetime.fromtimestamp(os.path.getmtime(path))


def convert_to_jpg(path):
    name, ext = os.path.splitext(path)

    if ext.lower() in [".jpg", ".jpeg"]:
        return path

    img = Image.open(path)

    min_alpha = img.convert("RGBA").getextrema()[-1][0]
    if min_alpha < 255:
        raise ValueError("Image contains transparency")

    img_rgb = img.convert("RGB")
    new_path = f"{name}.jpg"
    img_rgb.save(new_path)

    os.remove(path)

    return new_path


def load_exif(path):
    try:
        return piexif.load(path)
    except:
        return None


def save_exif(exif, path):
    exif_bytes = piexif.dump(exif)
    piexif.insert(exif_bytes, path)


def validate_exif_time(exif):
    if piexif.ImageIFD.DateTime not in exif["0th"]:
        return False
    if piexif.ExifIFD.DateTimeDigitized not in exif["Exif"]:
        return False
    if piexif.ExifIFD.DateTimeOriginal not in exif["Exif"]:
        return False

    return True


def set_exif_time(exif, time):
    time = time.strftime("%Y:%m:%d %H:%M:%S")
    exif["0th"][piexif.ImageIFD.DateTime] = time
    exif["Exif"][piexif.ExifIFD.DateTimeDigitized] = time
    exif["Exif"][piexif.ExifIFD.DateTimeOriginal] = time


def set_photo_exif_time(file_path, log=print):
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in IMAGE_FORMAT:
        return

    try:
        exif = load_exif(file_path)
        if exif:
            if validate_exif_time(exif):
                return

            set_exif_time(exif, get_os_time(file_path))
            save_exif(exif, file_path)
        else:
            exif = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
            set_exif_time(exif, get_os_time(file_path))
            file_path = convert_to_jpg(file_path)
            save_exif(exif, file_path)

        log(f'Updated: "{os.path.basename(file_path)}"')

    except:
        log(f'Error: "{os.path.basename(file_path)}"')


def set_photos_exif_time(folder_path, log=print):
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            set_photo_exif_time(file_path, log)
