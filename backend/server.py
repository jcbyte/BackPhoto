import asyncio
import json
import time
from pathlib import Path
from typing import Literal, TypedDict

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
        folder_path = Path(".", f".temp_{now}")
        folder_path.mkdir()

        # Find and move/copy all photos from ADB device to working folder
        yield format_yield(BackupYield(log=LogEntry(content="Scanning device")))
        try:
            for y in scanner.scan_device(folder_path, app.state.adb, body.config):
                yield format_yield(y)
        except Exception as e:
            yield error_yield(e)
            return
        # self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(33 if self.controller.config.set_time else 50))

        # # Modify photo time in EXIF if required
        # if self.controller.config.set_time:
        #     self.log_thread_safe("\nSetting photo time in EXIF...")
        #     photo_tools.set_photos_exif_time(folder_path, self.log_thread_safe)
        #     self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(67))

        # # Move photos from working folder to destination
        # self.log_thread_safe("\nMoving to destination...")
        # file_tools.move(folder_path, Path(self.controller.config.destination), now, self.log_thread_safe)
        # self.controller.update_gui_thread_safe(lambda: self.progress_bar_var.set(100))

        # # Remove temporary files if required
        # if self.controller.config.delete_temporary_files:
        #     self.log_thread_safe("\nRemoving temporary files...")
        #     shutil.rmtree(folder_path)

        # self.log_thread_safe("\nComplete!")
        # self.controller.update_gui_thread_safe(lambda: self.start_button.config(state="active"))

        # i = 0
        # for i in range(3):
        #     i += 1
        #     yield f"data: Update {i}\n\n"  # Each message must start with 'data:' and end with double newline
        #     await asyncio.sleep(1)  # simulate periodic updates

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
