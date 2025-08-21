from pathlib import PurePosixPath

from ppadb.client import Client as AdbClient
from ppadb.device import Device as AdbDevice


class Device:
    def __init__(self, device: AdbDevice) -> None:
        self.device = device

    def friendly_name(self) -> str:
        manufacturer = (self.device.shell("getprop ro.product.manufacturer") or "unknown").strip().title()
        model = (self.device.shell("getprop ro.product.model") or "unknown").strip()

        return f"{manufacturer} {model}"

    def ls(self, path: PurePosixPath) -> list[PurePosixPath]:
        dir_listing = (self.device.shell(f'ls "{path.as_posix()}" -1') or "").splitlines()
        return [path / item for item in dir_listing]

    def is_dir(self, path: PurePosixPath) -> bool:
        result = (d.device.shell(f'stat -c %F "{path.as_posix()}"') or "").strip()
        return result == "directory"

    def __str__(self) -> str:
        return f"{self.device.serial} ({self.friendly_name()})"


class ADB:
    def __init__(self, host="127.0.0.1", port=5037) -> None:
        self.client = AdbClient(host=host, port=port)

    def get_devices(self) -> list[Device]:
        return [Device(adbDevice) for adbDevice in self.client.devices()]
