import os
from pathlib import Path, PurePosixPath
from typing import Optional

from ppadb.client import Client as AdbClient
from ppadb.device import Device as AdbDevice


class Device:
    def __init__(self, device: AdbDevice) -> None:
        self.device = device

    @property
    def serial(self) -> str:
        return self.device.serial

    @property
    def friendly_name(self) -> str:
        """Get a user friendly name for the connected device."""

        manufacturer = (self.device.shell("getprop ro.product.manufacturer") or "unknown").strip().title()
        model = (self.device.shell("getprop ro.product.model") or "unknown").strip()

        return f"{manufacturer} {model}"

    def shell(self, cmd: str) -> str | None:
        """Send a shell command to the device."""

        return self.device.shell(cmd)

    def __str__(self) -> str:
        return f"{self.device.serial} ({self.friendly_name})"


class DevicePath:
    def __init__(self, device: Device, path: str | PurePosixPath, is_dir: Optional[bool] = None) -> None:
        self.device = device
        self._path = PurePosixPath(path)
        self._is_dir = is_dir

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def suffix(self) -> str:
        return self._path.suffix

    @property
    def path(self) -> str:
        return self._path.as_posix()

    def exists(self) -> bool:
        result = self.device.shell(f'test -e "{self.path}" && echo 1 || echo 0')
        return result == "1"

    @property
    def is_dir(self) -> bool:
        """Returns if the the given path is a directory."""

        if self._is_dir is None:
            ptype = (self.device.shell(f'stat -c %F "{self.path}/"') or "").strip()
            self._is_dir = ptype == "directory"

        return self._is_dir

    def list(self) -> list["DevicePath"]:
        """List the files and folders at the given path."""

        if not self.is_dir:
            raise NotADirectoryError

        # Redirect errors to null to avoid showing "No such file or output directory" as a file
        dir_listing = (self.device.shell(f'ls "{self.path}/" -p -1 2>/dev/null') or "").splitlines()
        return [DevicePath(self.device, self._path / item.replace("\\ ", " "), item.endswith("/")) for item in dir_listing]

    def copy(self, dst: Path):
        """Copy the file from the ADB device onto the host machine."""

        self.device.device.pull(self.path, dst)

    def copy2(self, dst: Path):
        """Copy the file from the ADB device onto the host machine whilst keeping timestamp metadata."""

        mtime_str = (self.device.shell(f'stat -c %Y "{self.path}"') or "").strip()
        mtime = int(mtime_str)
        self.copy(dst)
        os.utime(dst, (mtime, mtime))

    def remove(self):
        """Remove the file from the ADB device."""

        self.device.shell(f'rm "{self.path}"')

    def cut(self, dst: Path):
        """Cut the file from the ADB device onto the host machine."""

        self.copy(dst)
        self.remove()

    def cut2(self, dst: Path):
        """Cut the file from the ADB device onto the host machine whilst keeping timestamp metadata."""

        self.copy2(dst)
        self.remove()

    def __truediv__(self, other: "DevicePath|PurePosixPath|str") -> "DevicePath":

        if isinstance(other, DevicePath):
            if self.device.device.serial != other.device.device.serial:
                raise ValueError("Must be the same device")

        other_path = other.path if isinstance(other, DevicePath) else other

        return DevicePath(self.device, self._path / other_path)

    def __str__(self) -> str:
        return f"{self.path} @ {self.device}"


class ADB:
    def __init__(self, host="127.0.0.1", port=5037) -> None:
        self.client = AdbClient(host=host, port=port)

    def get_devices(self) -> list[Device]:
        return [Device(adbDevice) for adbDevice in self.client.devices()]
