import asyncio
import time

from adb import ADB
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

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
        return {"devices": [{"serial": device.serial, "name": device.friendly_name} for device in devices]}
    except:
        raise HTTPException(status_code=400, detail="Could not connect to ADB server")


@app.get("/backup")
async def backup():
    # todo this
    async def event_generator():
        i = 0
        for i in range(3):
            i += 1
            yield f"data: Update {i}\n\n"  # Each message must start with 'data:' and end with double newline
            await asyncio.sleep(1)  # simulate periodic updates

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
