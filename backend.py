import threading

from fastapi import FastAPI, Request
from uvicorn import run
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from os import environ
from typing import Dict, Any

from video_stream import make_photo, generate, vs


app = FastAPI()
app.mount('/js', StaticFiles(directory="gui/js"), name="js")
templates = Jinja2Templates(directory="gui/html")

if not environ.get('no_rpi', False):
    from my_i2c import MyI2CBus
    from bme280 import BME280
    from ms5611 import MS5611

    my_i2c_bus = MyI2CBus(1)
    my_i2c_bus["inside"] = BME280(my_i2c_bus)
    # my_i2c_bus["outside"] = MS5611(my_i2c_bus)
    dummy = False
else:
    dummy = True


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})


class UpdateResponse(BaseModel):
    inside: Dict[str, Any]
    outside: Dict[str, Any]


@app.get("/video")
async def video_feed():
    # return the response generated along with the specific media
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace;boundary=frame")


@app.get("/update", response_model=UpdateResponse)
async def update():
    data = {}
    if not dummy:
        t, p, h = my_i2c_bus['inside'].read_all()
        data['inside'] = {
            'temperature': t,
            'pressure': round(p, 2),
            'humidity': round(h, 2)
        }

        # p, t = my_i2c_bus['outside'].read_all()
        data['outside'] = {
            'temperature': round(t, 2),
            'pressure': round(p, 2),
        }
    else:
        data['inside'] = {
            'temperature': -40,
            'pressure': 560,
            'humidity': 2
        }
        data['outside'] = {
            'temperature': 26,
            'pressure': 1008,
            'humidity': 55
        }
    return data


if __name__ == '__main__':
    video_t = threading.Thread(target=make_photo)
    video_t.daemon = True
    video_t.start()

    run(app=app, port=8888)

vs.stop()
