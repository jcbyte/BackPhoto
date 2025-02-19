# <img src="icon.png" height="40"> &nbsp;BackPhoto

Windows application for backing up photos from your **MTP (Android) Device**.

The app scans a connected MTP device for specific files (based on their file extension), updates the EXIF information on photos to ensure the correct timestap, then organises them into a local (or remote) folder.

## Installation

Precompiled binaries for **Windows** are are available in [Releases](https://github.com/jcbyte/backPhoto/releases).

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start local app:

```bash
python app.py
```

## Build

To create a standalone executable use `PyInstaller`:

```bash
pyinstaller --onefile --windowed --icon=icon.png app.py
```

## Licence

[Apache License 2.0](LICENSE)
