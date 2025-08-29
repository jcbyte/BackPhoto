import asyncio
import json
import shutil
import time
from pathlib import Path
from typing import Literal, TypedDict

import file_tools
import photo_tools
import scanner
from adb import ADB
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typings import BackupYield, LogEntry, UserConfig

app = FastAPI()

app.state.adb = None


@app.get("/connect")
async def connect(host: str = Query("127.0.0.1", description="ADB server host"), port: int = Query(5037, description="ADB server port")):
    app.state.adb = ADB(host, port)

    if not app.state.adb.is_alive():
        raise HTTPException(status_code=400, detail="Could not connect to ADB server")

    return {}


@app.get("/devices")
async def devices():
    if app.state.adb is None:
        raise HTTPException(status_code=400, detail="ADB is not initialised")

    try:
        devices = app.state.adb.get_devices()

        return {
            "devices": [
                {
                    "serial": device.serial,
                    "authorised": device.authorised,
                    **({"name": device.friendly_name} if device.authorised else {}),
                }
                for device in devices
            ]
        }

    except:
        raise HTTPException(status_code=400, detail="Could not connect to ADB server")


class BackupBody(BaseModel):
    config: UserConfig


@app.get("/backup")
async def backup(body: BackupBody):
    if app.state.adb is None:
        raise HTTPException(status_code=400, detail="ADB is not initialised")

    class StreamedBackupLogEntry(BaseModel):
        timestamp: int
        type: Literal["info", "success", "error", "warning"]
        content: str

    class StreamedBackupResponse(BaseModel):
        progress: float | None = None
        log: StreamedBackupLogEntry | None = None

    def format_yield(obj: BackupYield) -> str:
        log_entry = obj.log
        if log_entry is not None:
            log_entry = StreamedBackupLogEntry(timestamp=int(time.time()), type=log_entry.type, content=log_entry.content)

        response = StreamedBackupResponse(
            progress=obj.progress,
            log=log_entry,
        )
        return f"data: {response.model_dump_json(exclude_none=True)}\n\n"

    def error_yield(e: Exception):
        return f"event: error\ndata: {str(e)}\n\n"

    async def event_generator():
        # todo progress updates

        # Create temporary working folder
        now = time.strftime("%Y-%m-%d_%H-%M-%S")
        # folder_path = Path(".", f".temp_{now}")
        # folder_path.mkdir()
        folder_path = Path(".", ".temp_2025-08-29_13-53-31")

        # Find and move/copy all photos from ADB device to working folder
        yield format_yield(BackupYield(log=LogEntry(content="Scanning device...")))
        try:
            for y in scanner.scan_device(folder_path, app.state.adb, body.config):
                yield format_yield(y)
        except Exception as e:
            yield error_yield(e)
            return
        yield format_yield(BackupYield(log=LogEntry(content="Device scan completed")))
        # self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(33 if self.controller.config.set_time else 50))

        # Modify photo time in EXIF if required
        if body.config.setExif:
            yield format_yield(BackupYield(log=LogEntry(content="Setting photo time in EXIF...")))
            try:
                for y in photo_tools.set_photos_exif_time(folder_path):
                    yield format_yield(y)
            except Exception as e:
                yield error_yield(e)
                return
            yield format_yield(BackupYield(log=LogEntry(content="Completed EXIF update")))
            # self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(67))

        # Move photos from working folder to destination
        yield format_yield(BackupYield(log=LogEntry(content="Moving files to destination")))
        try:
            for y in file_tools.move(folder_path, Path(body.config.destinationPath), now):
                yield format_yield(y)
        except Exception as e:
            yield error_yield(e)
            return
        yield format_yield(BackupYield(log=LogEntry(content="Moving files completed")))
        # self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(100))

        # Remove temporary files if required
        if body.config.removeTempFiles:
            yield format_yield(BackupYield(log=LogEntry(content="Removing temporary files...")))
            shutil.rmtree(folder_path)
            yield format_yield(BackupYield(log=LogEntry(content="Temporary files removed")))

        yield format_yield(BackupYield(log=LogEntry(content="Complete!", type="success")))

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
