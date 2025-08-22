# <img src="icon.png" height="40"> &nbsp;BackPhoto

Windows application for backing up photos from your **Android Device**.

The app uses ADB and scans a connected device for specific files (based on their file extension), updates the EXIF information on photos to ensure the correct timestamp, then organises them into a destination folder.

## ADB Setup

This app requires an ADB server running on `127.0.0.1:5037` (the default address).

1. Install ADB on your system: [Guide for Windows, macOS, and Linux](https://www.xda-developers.com/install-adb-windows-macos-linux/)
2. Start the ADB server by running `adb start-server`
3. After you finish using the application, stop the ADB server with `adb kill-server`

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
