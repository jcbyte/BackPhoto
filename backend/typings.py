from typing import Literal, TypedDict

from pydantic import BaseModel


class UserConfig(BaseModel):
    adbDevice: str | None = None
    destinationPath: str
    ignoredDirs: list[str]
    fileTypes: list[str]
    setExif: bool
    skipDot: bool
    moveFiles: bool
    removeTempFiles: bool


class LogEntry(BaseModel):
    type: Literal["info", "success", "error", "warning"] = "info"
    content: str


class BackupYield(BaseModel):
    progress: float | None = None
    log: LogEntry | None = None
