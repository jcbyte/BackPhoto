# <img src="icon.png" height="40"> &nbsp;BackPhoto

Simple app for backing up photos from your **MTP (Android) Device**.

This app scans a connected MTP device for specific files (based on their file extension), updates the EXIF information on photos to ensure the correct timestap and then organises them into a local (or remote) folder.

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

## Tech Stack

Python, Tkinter

## Authors

- [@jcbyte](https://www.github.com/jcbyte)
